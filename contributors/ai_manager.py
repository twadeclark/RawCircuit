import json
import random
from contributors.hugging_face_interface import HuggingFaceInterface
from contributors.local_openai_interface import LocalOpenAIInterface

class AIManager:
    def __init__(self):
        self.interface_list = {
            'LocalOpenAIInterface': LocalOpenAIInterface(),
            'HuggingFaceInterface': HuggingFaceInterface()
        }

        with open('models.json', 'r', encoding='utf-8') as file:
            self.models_json = json.load(file)

        self.model = None
        self.interface = None

    def choose_random_ai_unit(self):
        model_names = list(self.models_json.keys())
        model_name = random.choice(model_names)
        self._select_and_prepare_model(model_name)

    def choose_specific_ai_unit(self, model_name):
        self._select_and_prepare_model(model_name)

    def _select_and_prepare_model(self, model_name):
        self.model = self.models_json[model_name]
        interface_name = self.model['interface']
        self.interface = self.interface_list.get(interface_name)
        self.interface.prepare_model(self.model)

    def get_model(self):
        return self.model

    def get_model_name(self):
        return self.model['model_name']

    def get_model_polite_name(self):
        return self.model['polite_name']

    def generate_comment(self, user_content, system_content):
        return self.interface.generate_comment(user_content, system_content)

    def get_summary(self, article_text):
        return self.interface.generate_summary(article_text)

    def generate_comment_preformatted_message(self, instructions):
        return self.interface.generate_comment_preformatted_message(instructions)

    def generate_comment_preformatted_message_streaming(self, instructions):
        return self.interface.generate_comment_preformatted_message_streaming(instructions)

    def generate_new_comment_from_summary_and_previous_comment(self, instructions, summary_text, previous_comment):
        return self.interface.generate_new_comment_from_summary_and_previous_comment(instructions, summary_text, previous_comment)

