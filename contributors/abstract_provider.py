from abc import ABC, abstractmethod

class AbstractProvider(ABC):
    @abstractmethod
    def generate_comment(self, article, instructions):
        pass
