from abc import ABC, abstractmethod
from article import Article

class NewsAggregator(ABC):
    @abstractmethod
    def get_article(self) -> Article:
        pass