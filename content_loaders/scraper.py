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

def extract_pure_text_from_raw_html(html):
    text = strip_html_tags(html)
    text = remove_multiple_hashes(text)
    text = remove_all_quote(text)
    text = remove_extra_whitespace(text)

    return text

def strip_html_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    text = soup.get_text()
    return text

def remove_extra_whitespace(text):
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")
    text = " ".join(text.split())
    text = text.strip()
    return text

def remove_multiple_hashes(text):
    # text = re.sub(r'#+(?![\s])', '', text)
    return text

def remove_all_quote(text):
    text = re.sub(r'[\'"`“”‘’]', '', text)
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

def get_article_text_based_on_content_hint(article_to_process_content, raw_html):
    # this is all specific to only some news.api article content
    try:
        plus_chars = extract_last_integer(article_to_process_content)
        content_truncated = article_to_process_content.split('…', 1)[0]
        full_article = extract_article(raw_html, content_truncated, plus_chars)

        if full_article is None or len(full_article) == 0: # then we extract pure text and try again
            full_article = extract_article(extract_pure_text_from_raw_html(raw_html), extract_pure_text_from_raw_html(content_truncated), plus_chars)

        return full_article
    except Exception:
        return None
