from abc import ABC, abstractmethod

class AbstractProvider(ABC):
    @abstractmethod
    def generate_comment(self, user_content, system_content):
        pass

    @abstractmethod
    def generate_summary(self, article_text):
        pass

    @abstractmethod
    def prepare_model(self, model):
        pass
