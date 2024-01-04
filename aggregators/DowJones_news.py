# DowJones_news.py
from article import Article
from .base_aggregator import NewsAggregator

class DowJones_news(NewsAggregator):
    def get_article(self) -> Article:
        aggregator_name = "DowJones_news"
        article_url = "http://example.com/article"
        article_content = "This is the content of the article from DowJones_news."

        article = Article(aggregator_name, article_url, article_content)

        return article
    