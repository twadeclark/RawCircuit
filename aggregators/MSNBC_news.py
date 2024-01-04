# MSNBC_news.py
from article import Article
from .base_aggregator import NewsAggregator

class MSNBC_news(NewsAggregator):
    def get_article(self) -> Article:
        aggregator_name = "MSNBC_news"
        article_url = "http://example.com/article"
        article_content = "This is the content of the article from MSNBC_news."

        article = Article(aggregator_name, article_url, article_content)

        return article
    