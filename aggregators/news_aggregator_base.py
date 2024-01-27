from abc import ABC, abstractmethod

class NewsAggregator(ABC):
    @abstractmethod
    def fetch_articles(self):
        pass

    @abstractmethod
    def get_name(self):
        pass
