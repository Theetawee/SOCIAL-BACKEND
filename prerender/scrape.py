import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


def scrape_url(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navigate to the page
        driver.get(url)

        # Wait for the body to load (indicating the page has loaded)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Keep scrolling until no more dynamic content is loaded
        scroll_pause_time = 2
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for new content to load
            time.sleep(scroll_pause_time)

            # Check if additional content was loaded by comparing heights
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Ensure all React components and lazy-loaded content is fully rendered
        time.sleep(3)

        # Return the entire page content
        page_source = driver.page_source

        return page_source

    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return f"Error scraping the page: {str(e)}"

    finally:
        driver.quit()
