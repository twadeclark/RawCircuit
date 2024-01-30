from abc import ABC, abstractmethod

class AbstractAIUnit(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def prepare_model(self, model):
        pass

    @abstractmethod
    def generate_summary(self, article_text):
        pass

    @abstractmethod
    def generate_comment_preformatted_message_streaming(self, message_text):
        pass

    @abstractmethod
    def generate_new_comment_from_summary_and_previous_comment(self, instructions, summary_text, previous_comment):
        pass



    # @abstractmethod
    # def generate_comment(self, user_content, system_content):
    #     pass

    # @abstractmethod
    # def generate_comment_preformatted_message(self, message_text):
    #     pass
