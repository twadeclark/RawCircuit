import random
from database.db_manager import DBManager
from .newsapiorg_news import NewsApiOrgNews

class NewsAggregatorManager:
    def __init__(self):
        self.aggregators = [ # Put the list of aggregators here
            NewsApiOrgNews(),
        ]
        self.aggregator = random.choice(self.aggregators)

    def get_article(self, query_term):
        return self.aggregator.get_article(query_term)

    def get_article_(self, query_term):
        return self.aggregator.get_article(query_term)


    def get_random_article(self):
        db_manager = DBManager()
        return db_manager.get_random_article()
