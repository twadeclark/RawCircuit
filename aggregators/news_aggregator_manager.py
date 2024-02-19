import datetime
import random
# from aggregators.rss_feeder import RSSFeeder
from article import Article
from error_handler import FatalError
from .newsapiorg_news import NewsApiOrgNews

class NewsAggregatorManager:

    def __init__(self, config, db_manager, aggregator_name=None):
        self.db_manager = db_manager
        self.aggregators = [
            NewsApiOrgNews(config["NewsAPI"]),
            # RSSFeeder(config["RSSFeeder"]),
        ]
        if not aggregator_name:
            self.aggregator = random.choice(self.aggregators)
        else:
            self.aggregator = self.get_aggregator_by_name(aggregator_name)

    def get_aggregator_by_name(self, aggregator_name):
        for aggregator in self.aggregators:
            if aggregator.get_name() == aggregator_name:
                return aggregator
        return None

    def fetch_new_articles_into_db(self):
        articles = self.aggregator.fetch_articles()
        rec_order = 0
        for article in articles["articles"]:
            if self.db_manager.article_exists(article["url"]):
                continue

            article = Article(
                None,
                self.aggregator.get_name(),
                article["source"]["id"],
                article["source"]["name"],
                article["author"],
                article["title"],
                article["description"],
                article["url"],
                article["urlToImage"],
                article["publishedAt"],
                article["content"],
                None,
                None,
                None,
                None,
                None
            )

            article.added_timestamp = datetime.datetime.now()
            article.rec_order = rec_order
            self.db_manager.save_article(article)
            rec_order += 1
        return rec_order

    def update_scrape_time(self, article):
        self.db_manager.update_scrape_time(article)

    def update_scraped_website_content(self, article):
        self.db_manager.update_scraped_website_content(article)
