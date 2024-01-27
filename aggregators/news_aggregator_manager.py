import random
from database.db_manager import DBManager
from .newsapiorg_news import NewsApiOrgNews

class NewsAggregatorManager:
    def __init__(self):
        self.db_manager = DBManager()
        self.aggregators = [ # Put the list of aggregators here
            NewsApiOrgNews(),
        ]
        self.aggregator = random.choice(self.aggregators)

    def get_random_article(self):
        return self.db_manager.get_random_article()

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
