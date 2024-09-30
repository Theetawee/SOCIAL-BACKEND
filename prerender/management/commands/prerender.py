import concurrent.futures
import json
import logging
import queue
import re
import time
from contextlib import contextmanager

from django.conf import settings
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from accounts.models import Account
from main.models import Post
from prerender.models import ScrapedContent

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Prerender React pages, minify HTML, and store their content using concurrent processing"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver_queue = queue.Queue()
        self.initialize_driver_pool(max_drivers=5)

    def initialize_driver_pool(self, max_drivers):
        """Initialize a pool of WebDriver instances."""
        for _ in range(max_drivers):
            self.driver_queue.put(self.create_driver())

    def create_driver(self):
        """Create and configure a new Chrome WebDriver instance."""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-crash-reporter")
        chrome_options.add_argument("--disable-oopr-debug-crash-dump")
        chrome_options.add_argument("--no-crash-upload")
        chrome_options.add_argument("--disable-low-res-tiling")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def wait_for_react(self, driver, timeout=30):
        """Wait for React to finish rendering."""
        script = """
        return (window.React && window.React.version) ? Object.keys(window).length ===Object.keys(window).filter(key => !key.startsWith('_')).length :true;
        """
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script(script))

    def wait_for_network_idle(self, driver, timeout=30, max_connections=0):
        """Wait for network to become idle (no active requests)."""
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                """
                return window.performance.getEntriesByType('resource').filter(
                    e => !e.responseEnd && e.initiatorType === 'xmlhttprequest'
                ).length <= arguments[0];
            """,
                max_connections,
            )
        )

    def wait_for_loader_to_disappear(self, driver, timeout=30):
        """Wait for any loading indicators to disappear."""
        try:
            WebDriverWait(driver, timeout).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#id_loader"))
            )
        except TimeoutException:
            self.stdout.write(
                self.style.WARNING("Loader did not disappear, continuing anyway.")
            )

    def scroll_to_bottom(self, driver):
        """Scroll to the bottom of the page and wait for content to load."""
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for potential new content to load
            self.wait_for_react(
                driver
            )  # Wait for React to finish rendering any new content
            self.wait_for_network_idle(
                driver
            )  # Wait for any triggered requests to complete
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def minify_html(self, html):
        """Minify HTML content."""
        html = re.sub(r"<!--(?!<!)[^\[>][\s\S]*?-->", "", html)
        html = re.sub(
            r"(<style[^>]*>)(.*?)(</style>)",
            self.minify_css,
            html,
            flags=re.DOTALL | re.IGNORECASE,
        )
        html = re.sub(
            r"(<script[^>]*>)(.*?)(</script>)",
            self.minify_js,
            html,
            flags=re.DOTALL | re.IGNORECASE,
        )
        html = re.sub(
            r'(<script type="application/ld\+json">)(.*?)(</script>)',
            self.minify_json_ld,
            html,
            flags=re.DOTALL | re.IGNORECASE,
        )
        html = re.sub(r">\s+<", "><", html)
        html = re.sub(r"\s+", " ", html)
        return html.strip()

    def minify_css(self, match):
        """Minify CSS content."""
        style_tag, content, closing_tag = match.groups()
        content = re.sub(r"/\*[\s\S]*?\*/", "", content)  # Remove CSS comments
        content = re.sub(r"\s+", " ", content)  # Remove extra whitespace
        content = re.sub(
            r"\s*([{:;}])\s*", r"\1", content
        )  # Remove spaces around CSS rules
        return f"{style_tag}{content.strip()}{closing_tag}"

    def minify_js(self, match):
        """Minify JavaScript content while preserving URLs."""
        script_tag, content, closing_tag = match.groups()
        url_placeholders = {}

        def replace_url(m):
            placeholder = f"__URL_PLACEHOLDER_{len(url_placeholders)}__"
            url_placeholders[placeholder] = m.group(0)
            return placeholder

        content = re.sub(r"(https?:)?//[^\s/$.?#].[^\s]*", replace_url, content)
        content = re.sub(
            r"(?<!:)//.*?$", "", content, flags=re.MULTILINE
        )  # Remove single-line comments
        content = re.sub(r"/\*[\s\S]*?\*/", "", content)  # Remove multi-line comments
        content = re.sub(r"\s+", " ", content)  # Remove extra whitespace

        for placeholder, url in url_placeholders.items():
            content = content.replace(placeholder, url)

        return f"{script_tag}{content.strip()}{closing_tag}"

    def minify_json_ld(self, match):
        """Minify JSON-LD content."""
        script_tag, content, closing_tag = match.groups()
        try:
            minified_json = json.dumps(json.loads(content), separators=(",", ":"))
            return f"{script_tag}{minified_json}{closing_tag}"
        except json.JSONDecodeError:
            return match.group(0)

    @contextmanager
    def get_driver(self):
        """Context manager to handle driver reuse."""
        driver = self.driver_queue.get()
        try:
            yield driver
        finally:
            self.driver_queue.put(driver)

    def scrape_url(self, url):
        """Scrape a single URL, ensuring all React content is rendered."""
        with self.get_driver() as driver:
            try:
                driver.get(url)
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "alloqet"))
                )
                self.wait_for_react(driver)
                self.wait_for_network_idle(driver)
                self.scroll_to_bottom(driver)
                self.wait_for_loader_to_disappear(driver)
                self.wait_for_network_idle(driver)
                self.wait_for_react(driver)

                page_source = driver.page_source
                minified_html = self.minify_html(page_source)

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully scraped and minified: {url}")
                )
                return url, minified_html

            except Exception as e:
                error_message = f"Error scraping {url}: {str(e)}"
                logger.error(error_message)
                self.stdout.write(self.style.ERROR(error_message))
                return url, None

    def store_content(self, url, content):
        """Store or update scraped content in the database."""
        ScrapedContent.objects.update_or_create(url=url, defaults={"content": content})

    def get_urls_to_scrape(self):
        """Generate all URLs to be scraped."""
        base_url = getattr(settings, "BASE_URL", "https://www.alloqet.com")
        urls = ["/", "/i/login", "/i/signup", "/add", "/search"]
        urls.extend([f"/status/{post.id}" for post in Post.objects.all()])
        urls.extend([f"/{account.username}" for account in Account.objects.all()])
        return [f"{base_url}{url}" for url in urls]

    def handle(self, *args, **options):
        """Main command handler."""
        urls = self.get_urls_to_scrape()
        self.stdout.write(
            self.style.WARNING(f"Starting to scrape and minify {len(urls)} URLs...")
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self.scrape_url, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url, content = future.result()
                if content:
                    self.store_content(url, content)

        self.stdout.write(self.style.SUCCESS("Finished scraping and minifying URLs."))
