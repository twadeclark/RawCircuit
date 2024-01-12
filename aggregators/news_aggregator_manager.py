import random
from database.db_manager import DBManager
from .newsapiorg_news import NewsApiOrgNews

class NewsAggregatorManager:
    def __init__(self):
        self.aggregators = [ # Put the list of aggregators here
            NewsApiOrgNews(),
        ]

    def get_article(self):
        aggregator = random.choice(self.aggregators)
        return aggregator.get_article()

    def get_random_article(self):
        db_manager = DBManager()
        return db_manager.get_random_article()
