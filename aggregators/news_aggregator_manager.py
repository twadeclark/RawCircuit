import random
from .newsapiorg_news import newsapiorg_news

class NewsAggregatorManager:
    def __init__(self):
        self.aggregators = [ # Put the list of aggregators here
            newsapiorg_news(),
        ]

    def get_article(self):
        # Randomly select an aggregator and fetch an article
        aggregator = random.choice(self.aggregators)
        return aggregator.get_article()
