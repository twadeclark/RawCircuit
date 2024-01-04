# base_aggregator.py
from abc import ABC, abstractmethod

class NewsAggregator(ABC):
    @abstractmethod
    def get_article(self):
        pass
    