import random
from aggregators.rss_feeder import RSSFeeder
from database.db_manager import DBManager
from .newsapiorg_news import NewsApiOrgNews

class NewsAggregatorManager: # we want to be able to choose an aggregator at random, or send in the name of the aggregator we want to use

    def __init__(self, aggregator_name=None):
        self.db_manager = DBManager()
        self.aggregators = [ # Put the list of aggregators here
            NewsApiOrgNews(),
            RSSFeeder(),
        ]
        if aggregator_name is not None:
            self.aggregator = self.get_aggregator_by_name(aggregator_name)
        else:
            self.aggregator = random.choice(self.aggregators)

    def get_aggregator_by_name(self, aggregator_name):
        for aggregator in self.aggregators:
            if aggregator.get_name() == aggregator_name:
                return aggregator
        return None

    def fetch_new_articles_into_db(self):
        articles = self.aggregator.fetch_articles()
        rec_order = 0
        for article in articles:
            article.rec_order = rec_order
            self.db_manager.save_article(article)
            rec_order += 1

    def get_next_article_to_process(self):
        return self.db_manager.get_next_article_to_process()
    
    def update_scrape_time(self, article):
        self.db_manager.update_scrape_time(article)

    def update_process_time(self, article):
        self.db_manager.update_process_time(article)

    def update_scraped_website_content(self, article):
        self.db_manager.update_scraped_website_content(article)
