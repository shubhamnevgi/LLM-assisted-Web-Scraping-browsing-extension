from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import requests

def scrape_website(url, max_retries=3):
    """
    Scrape the content of a website using Selenium.

    Args:
        url (str): The URL of the website to scrape.
        max_retries (int): Maximum number of retries if scraping fails.

    Returns:
        str: The page source (HTML content) of the website, or None if scraping fails.
    """
    ua = UserAgent()

    for attempt in range(max_retries):
        try:
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in headless mode
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'user-agent={ua.random}')  # Set a random User-Agent

            # Use ChromeDriverManager to handle driver installation
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())

            # Initialize the WebDriver
            with webdriver.Chrome(service=service, options=chrome_options) as driver:
                driver.set_page_load_timeout(30)  # Set page load timeout
                driver.get(url)  # Navigate to the URL

                # Wait for the page to load
                time.sleep(5)

                # Return the page source (HTML content)
                return driver.page_source

        except WebDriverException as e:
            print(f"WebDriver error (Attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print("Max retries reached. Falling back to requests.")
                return fallback_scraper(url)

        except Exception as e:
            print(f"An unexpected error occurred (Attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print("Max retries reached. Falling back to requests.")
                return fallback_scraper(url)

    return None


def fallback_scraper(url):
    """
    Fallback scraper using requests if Selenium fails.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        str: The HTML content of the website, or None if scraping fails.
    """
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        response = requests.get(url, headers=headers, verify=False)  # Disable SSL verification
        response.raise_for_status()  # Raise an error for bad status codes
        return response.text
    except Exception as e:
        print(f"Fallback scraper error: {str(e)}")
        return None

def extract_body_content(html_content):
    """
    Extract the body content from the HTML.

    Args:
        html_content (str): The HTML content of the website.

    Returns:
        str: The content inside the <body> tag, or an empty string if extraction fails.
    """
    if html_content is None:
        return ""

    try:
        soup = BeautifulSoup(html_content, "html.parser")
        body_content = soup.body
        if body_content:
            return str(body_content)
    except Exception as e:
        print(f"Error extracting body content: {str(e)}")
    return ""


def clean_body_content(body_content):
    """
    Clean the body content by removing scripts, styles, and extra whitespace.

    Args:
        body_content (str): The raw body content of the website.

    Returns:
        str: The cleaned text content.
    """
    if not body_content:
        return ""

    try:
        soup = BeautifulSoup(body_content, "html.parser")

        # Remove script and style tags
        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()

        # Extract text and clean it
        cleaned_content = soup.get_text(separator="\n")
        cleaned_content = "\n".join(
            line.strip() for line in cleaned_content.splitlines() if line.strip()
        )

        return cleaned_content
    except Exception as e:
        print(f"Error cleaning body content: {str(e)}")
        return body_content


def split_dom_content(dom_content, max_length=6000):
    """
    Split the DOM content into chunks at logical boundaries.

    Args:
        dom_content (str): The DOM content to split.
        max_length (int): The maximum length of each chunk.

    Returns:
        list: A list of chunks, each no longer than max_length.
    """
    if not dom_content:
        return []

    chunks = []
    start = 0

    while start < len(dom_content):
        # Find the nearest logical boundary (e.g., end of a table row or product block)
        end = min(start + max_length, len(dom_content))
        if end < len(dom_content):
            # Try to split at the end of a line or a logical block
            boundary = dom_content.rfind("\n", start, end)
            if boundary > start:
                end = boundary + 1  # Include the newline character

        chunks.append(dom_content[start:end])
        start = end

    return chunks