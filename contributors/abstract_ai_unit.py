from abc import ABC, abstractmethod

class AbstractAIUnit(ABC):
    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def fetch_inference(self, model, formatted_messages, temperature):
        pass
