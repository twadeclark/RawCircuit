from abc import ABC, abstractmethod
# from article import Article

class NewsAggregator(ABC):
    @abstractmethod
    def fetch_articles(self):
        pass
