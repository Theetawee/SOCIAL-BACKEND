# In your Django app directory, create a new file: management/commands/prerender.py

import concurrent.futures
import logging
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from prerender.models import (
    ScrapedContent,
)  # Replace 'your_app' with your actual app name
from main.models import Post
from accounts.models import Account
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Prerender pages and store their content using concurrent processing"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver_pool = []

    def create_driver(self):
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

        driver = webdriver.Chrome(options=chrome_options)
        self.driver_pool.append(driver)
        return driver

    def scrape_url(self, url):
        driver = self.create_driver()
        try:
            driver.get(url)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            scroll_pause_time = 2
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            time.sleep(3)
            page_source = driver.page_source
            self.stdout.write(self.style.SUCCESS(f"Successfully scraped: {url}"))
            return url, page_source

        except Exception as e:
            error_message = f"Error scraping {url}: {str(e)}"
            logger.error(error_message)
            self.stdout.write(self.style.ERROR(error_message))
            return url, None

    def handle(self, *args, **options):
        base_url = getattr(settings, "BASE_URL", "https://www.alloqet.com")
        urls = ["/", "/i/login", "/i/signup", "/add", "/search"]
        urls.extend([f"/status/{post.id}" for post in Post.objects.all()])
        urls.extend([f"/{account.username}" for account in Account.objects.all()])

        full_urls = [f"{base_url}{url}" for url in urls]

        self.stdout.write(
            self.style.WARNING(f"Starting to scrape {len(full_urls)} URLs...")
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(self.scrape_url, url): url for url in full_urls
            }
            for future in concurrent.futures.as_completed(future_to_url):
                url, content = future.result()
                if content:
                    ScrapedContent.objects.update_or_create(
                        url=url, defaults={"content": content}
                    )

        self.stdout.write(self.style.SUCCESS("Prerendering completed"))

        # Close all browser instances
        for driver in self.driver_pool:
            driver.quit()

        self.stdout.write(self.style.SUCCESS("All browser instances closed"))
