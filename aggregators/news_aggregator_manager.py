import random
from aggregators.ABC_news import ABC_news
from aggregators.AP_news import AP_news
from aggregators.DowJones_news import DowJones_news
from aggregators.FinancialTimes_news import FinancialTimes_news
from aggregators.MSNBC_news import MSNBC_news


class NewsAggregatorManager:
    def __init__(self):
        self.aggregators = [
            ABC_news(),
            AP_news(),
            DowJones_news(),
            FinancialTimes_news(),
            MSNBC_news()
        ]

    def get_article(self):
        # Randomly select an aggregator and fetch an article
        aggregator = random.choice(self.aggregators)
        return aggregator.get_article()
