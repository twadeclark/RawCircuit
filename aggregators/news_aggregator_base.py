from abc import ABC, abstractmethod

class NewsAggregator(ABC):
    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def fetch_articles(self):
        pass

    @abstractmethod
    def get_name(self):
        pass
