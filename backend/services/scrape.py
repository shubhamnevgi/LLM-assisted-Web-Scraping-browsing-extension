from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

def is_valid_content(html_content, min_text_length=100):
    """
    Check if the fetched HTML has a <body> with sufficient text.
    """
    if not html_content:
        return False
    soup = BeautifulSoup(html_content, "html.parser")
    body = soup.body
    if body and len(body.get_text(strip=True)) >= min_text_length:
        return True
    return False

def simple_scrape(url):
    """
    Attempt to scrape the website using requests.
    """
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        # Note: verify can be set to True in production. Disabled here for convenience.
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Simple scraper error: {str(e)}")
        return None

def selenium_scrape(url, max_retries=3):
    """
    Scrape the website using Selenium with optimizations for faster execution.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import WebDriverException, TimeoutException
    from fake_useragent import UserAgent
    import time

    ua = UserAgent()
    for attempt in range(max_retries):
        try:
            chrome_options = Options()
            # Run in headless mode
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-plugins-discovery")
            # Disable images to speed up loading
            chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
            # Set the page load strategy to "eager" so Selenium returns once the DOM is ready
            chrome_options.page_load_strategy = "eager"
            # Set a random user agent
            chrome_options.add_argument(f'user-agent={ua.random}')

            # Use webdriver_manager for automatic driver management
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())

            with webdriver.Chrome(service=service, options=chrome_options) as driver:
                # Use implicit wait to avoid fixed sleep times
                driver.implicitly_wait(10)
                driver.set_page_load_timeout(30)
                driver.get(url)
                
                # Wait until document.readyState is 'complete'
                WebDriverWait(driver, 15).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                
                # If specific elements are required, use an explicit wait:
                # For example, wait for the <body> tag to be present
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_element(By.TAG_NAME, "body")
                )
                
                # Return the page source
                return driver.page_source
        except (WebDriverException, TimeoutException) as e:
            print(f"Selenium error (Attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return None
        except Exception as e:
            print(f"Unexpected Selenium error (Attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None
    return None

def scrape_website(url):
    """
    Attempt to scrape the website using a fast requests call first.
    If the content appears incomplete (i.e. dynamic site), use Selenium.
    """
    content = simple_scrape(url)
    if is_valid_content(content):
        print(f"Page source: {content}")
        return content
    else:
        print("Content appears incomplete; switching to Selenium for dynamic content.")
        content = selenium_scrape(url)
        print(f"Page source: {content}")
        return content

def extract_body_content(html_content):
    """
    Extract the content within the <body> tag.
    """
    if not html_content:
        return ""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        body = soup.body
        if body:
            print(f"body content: {body}")
            return str(body)
    except Exception as e:
        print(f"Error extracting body content: {str(e)}")
    return ""

def clean_body_content(body_content):
    """
    Remove scripts, styles, and extra whitespace from the body content.
    """
    if not body_content:
        return ""
    try:
        soup = BeautifulSoup(body_content, "html.parser")
        for tag in soup(["script", "style", "header", "footer", "nav", "aside", "form", "iframe", "noscript", "object", "embed", "link", "meta", "button", "input", "select", "textarea", "path", "svg", "img"]):
            tag.extract()
        
        # Remove unnecessary tag attributes
        for tag in soup.find_all(True):
            for attribute in ["style", "id", "onclick", "onload"]:
                if attribute in tag.attrs:
                    del tag.attrs[attribute]
            # Remove any attribute starting with 'data-'
            for attribute in list(tag.attrs):
                if attribute.startswith("data-"):
                    del tag.attrs[attribute]
        
        cleaned_html = str(soup)
        print(f"cleaned_text: {cleaned_html}")
        return cleaned_html
    except Exception as e:
        print(f"Error cleaning body content: {str(e)}")
        return body_content

# def split_dom_content(dom_content, max_length=500):  
#     if not dom_content:
#         return []
    
#     soup = BeautifulSoup(dom_content, "html.parser")
#     body = soup.body if soup.body else soup
#     blocks = list(body.children)
    
#     chunks = []
#     current_chunk = ""
#     for block in blocks:
#         block_html = str(block)
#         if len(current_chunk) + len(block_html) > max_length:
#             if current_chunk:
#                 chunks.append(current_chunk)
#                 current_chunk = block_html
#             else:
#                 # In case a single block exceeds max_length, add it as a separate chunk.
#                 chunks.append(block_html)
#                 current_chunk = ""
#         else:
#             current_chunk += block_html
#     if current_chunk:
#         chunks.append(current_chunk)
    
#     return chunks
