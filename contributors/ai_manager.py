import json
import random
from contributors.local_openai_interface import OpenAIInterface

class AIManager:
    def __init__(self):
        self.interface_list = {
            'OpenAIInterface': OpenAIInterface()
        }

        with open('models.json', 'r', encoding='utf-8') as file:
            self.models_json = json.load(file)

        self.model = None
        self.interface = None
        self.choose_random_provider()

    def choose_random_provider(self):
        model_names = list(self.models_json.keys())
        random_model_name = random.choice(model_names)
        self.model = self.models_json[random_model_name]
        interface_name = self.model['interface']
        self.interface = self.interface_list.get(interface_name)
        self.interface.prepare_model(self.model)

    def get_model(self):
        return self.model

    def get_model_polite_name(self):
        return self.model['polite_name']

    def generate_comment(self, user_content, system_content):
        return self.interface.generate_comment(user_content, system_content)

    def get_summary(self, article_text):
        return self.interface.generate_summary(article_text)
