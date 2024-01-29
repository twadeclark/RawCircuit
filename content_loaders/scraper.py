import re
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
    text = remove_extra_whitespace(text)

    return text

def remove_extra_whitespace(text):
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")
    text = " ".join(text.split())
    return text


def extract_last_integer(s):
    if not isinstance(s, str):
        return None

    matches = re.findall(r'\[\D*(\d+)\D*\]', s)

    if not matches:
        return None

    try:
        return int(matches[-1])
    except ValueError:
        return None

def extract_article(raw_text_extracted, content_truncated, plus_chars):
    try:
        if not all(isinstance(i, str) for i in [raw_text_extracted, content_truncated]) or not isinstance(plus_chars, int):
            return None

        start = raw_text_extracted.index(content_truncated)
        end = start + len(content_truncated) + plus_chars
        full_article = raw_text_extracted[start:end]

        return full_article
    except Exception:
        return None
