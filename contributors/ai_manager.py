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

    def choose_random_model_name(self):
        model_names = list(self.models_json.keys())
        model_name = random.choice(model_names)
        return model_name

    def fetch_inference(self, model_name, prompt): #TODO: get api_key from config file, do not store api_key in models.json
        model = self._return_model_by_name(model_name)
        interface_name = model['interface']
        interface = self.interface_list.get(interface_name)

        prompt_word_length = len(prompt.split())
        if (prompt_word_length * 2) > model["max_tokens"]: # if it's too long, we keep the first and last quarter of the prompt
            words = prompt.split()
            quarter_length = int(model["max_tokens"] / 4)
            prompt = " ".join(words[:quarter_length] + words[-quarter_length:])

        response = interface.fetch_inference(model, prompt) #TODO: send api_key also

        if response is not None and len(response) > 0: # this strips off the prompt if the response starts with the prompt
            prompt_length = len(prompt)
            if response[:prompt_length] == prompt:
                response = response[prompt_length:]

        return response.strip()

    def _return_model_by_name(self, model_name):
        model = self.models_json[model_name]
        return model






    # def get_model_polite_name(self, model):
    #     return model['polite_name']

    # def _select_and_prepare_model(self, model_name):
    #     model = self.models_json[model_name]
    #     interface_name = self.model['interface']
    #     self.interface = self.interface_list.get(interface_name)
    #     self.interface.prepare_model(self.model)

    # def get_summary(self, article_text, model_name):
    #     return self.interface.generate_summary(article_text, model_name)



    # def choose_random_ai_unit(self):
    #     model_names = list(self.models_json.keys())
    #     model_name = random.choice(model_names)
    #     self._select_and_prepare_model(model_name)





    # def choose_specific_ai_unit(self, model_name):
    #     self._select_and_prepare_model(model_name)

    # def get_model(self):
    #     return self.model

    # def get_model_name(self):
    #     return self.model['model_name']

    # def generate_comment(self, user_content, system_content):
    #     return self.interface.generate_comment(user_content, system_content)

    # def generate_comment_preformatted_message(self, instructions):
    #     return self.interface.generate_comment_preformatted_message(instructions)

    # def generate_comment_preformatted_message_streaming(self, instructions):
    #     return self.interface.generate_comment_preformatted_message_streaming(instructions)

    # def generate_new_comment_from_summary_and_previous_comment(self, instructions, summary_text, previous_comment):
    #     return self.interface.generate_new_comment_from_summary_and_previous_comment(instructions, summary_text, previous_comment)

    # def generate_new_comment_from_fully_formatted_prompt(self, prompt):
    #     return self.interface.generate_new_comment_from_fully_formatted_prompt(prompt)
