# ABC_news.py
from .base_aggregator import NewsAggregator
from article import Article

class ABC_news(NewsAggregator):
    def get_article(self) -> Article:
        aggregator_name = "ABC_news"
        article_url = "http://example.com/article"
        article_content = "This is the content of the article from ABC_news."

        article = Article(aggregator_name, article_url, article_content)

        return article
    