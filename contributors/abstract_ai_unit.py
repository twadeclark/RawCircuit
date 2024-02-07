from abc import ABC, abstractmethod

class AbstractAIUnit(ABC):

    @abstractmethod
    def fetch_inference(self, model, formatted_messages):
        pass
