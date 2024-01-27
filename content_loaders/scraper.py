from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def fetch_raw_html_from_url(url):
    driver = webdriver.Chrome()

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        html = driver.page_source
        return html, True
    except selenium.common.exceptions.WebDriverException as e:
        return str(e), False
    finally:
        driver.quit()

def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text
