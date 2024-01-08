import random
from .newsapiorg_news import newsapiorg_news
from database.db_manager import DBManager

class NewsAggregatorManager:
    def __init__(self):
        self.aggregators = [ # Put the list of aggregators here
            newsapiorg_news(),
        ]

    def get_article(self):
        # Randomly select an aggregator and fetch an article
        aggregator = random.choice(self.aggregators)
        return aggregator.get_article()

    # return the most recent article from the database that has not been processed
    def get_most_recent_article(self):
        db_manager = DBManager()
        return db_manager.get_most_recent_article()
