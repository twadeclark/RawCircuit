from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    # Setup WebDriver (using Chrome in this example)
    driver = webdriver.Chrome()

    try:
        # Open the webpage
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Extract text and remove any remaining HTML tags
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        # Return the cleaned text
        return text, True
    except Exception as e:
        return str(e), False

    finally:
        # Close the WebDriver
        driver.quit()

def extract_raw_html_from_url(url):
    # Setup WebDriver (using Chrome in this example)
    driver = webdriver.Chrome()

    try:
        # Open the webpage
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Get page source and parse with BeautifulSoup
        html = driver.page_source

        # Return the cleaned text
        return html, True
    except Exception as e:
        return str(e), False

    finally:
        # Close the WebDriver
        driver.quit()

def extract_text_from_html(html):
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    # Extract text and remove any remaining HTML tags
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    # Return the cleaned text
    return text

# def get_tag_cloud(text):
#     # Get the tag cloud
#     tag_cloud = TagCloud()
#     tag_cloud.get_tag_cloud(text)

#     # Return the tag cloud
#     return tag_cloud