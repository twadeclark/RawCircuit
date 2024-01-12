from abc import ABC, abstractmethod

class AbstractProvider(ABC):
    @abstractmethod
    def generate_comment(self, incoming_text, instructions):
        pass

    @abstractmethod
    def generate_summary(self, article_text):
        pass
