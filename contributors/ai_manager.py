import json
import random
import re
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

    def return_model_by_name(self, model_name):
        if model_name is None or len(model_name) == 0:
            model_name = self._choose_random_model_name()
        model = self.models_json[model_name]

        polite_name = re.sub(r'[^.\w]', ' ', model_name)
        polite_name = re.sub(r'_', ' ', polite_name)

        polite_name = polite_name.title()

        return polite_name, model

    def fetch_inference(self, model, formatted_messages): #TODO: get api_key from config file, do not store api_key in models.json
        # model = self.return_model_by_name(model_name)
        interface_name = model['interface']
        interface = self.interface_list.get(interface_name)


        word_limit = model["max_tokens"] // 2
        formatted_messages = adjust_content_based_on_user_entries(formatted_messages, word_limit)


        # let's go!
        response = interface.fetch_inference(model, formatted_messages) #TODO: send api_key also

        if response is not None and len(response) > 0: # this strips off the prompt if the response starts with the prompt
            prompt_length = len(formatted_messages)
            if response[:prompt_length] == formatted_messages:
                response = response[prompt_length:]

        return response.strip()

    def _choose_random_model_name(self):
        model_names = list(self.models_json.keys())
        model_name = random.choice(model_names)
        return model_name



# Function to calculate word count
def calculate_word_count(list_of_dicts):
    combined_string = " ".join(item["content"] for item in list_of_dicts)
    return len(combined_string.split())

# Function to reduce content size
def reduce_content(list_of_dicts, word_limit):
    while calculate_word_count(list_of_dicts) > word_limit:
        # Find the longest user content
        longest_user_content = None
        longest_user_index = -1
        for i, item in enumerate(list_of_dicts):
            if item["role"] == "user":
                if longest_user_content is None or len(item["content"].split()) > len(longest_user_content.split()):
                    longest_user_content = item["content"]
                    longest_user_index = i
        
        # Split and reduce the longest content
        if longest_user_content:
            words = longest_user_content.split()
            one_third_length = len(words) // 3
            reduced_content = ' '.join(words[:one_third_length] + words[-one_third_length:])
            list_of_dicts[longest_user_index]["content"] = reduced_content

    return list_of_dicts

def adjust_content_based_on_user_entries(list_of_dicts, word_limit):
    while calculate_word_count(list_of_dicts) > word_limit:
        user_entries = [item for item in list_of_dicts if item["role"] == "user"]
        user_entries_count = len(user_entries)

        # If there are 5 or more "user" entries, remove the middle one
        if user_entries_count >= 5:
            middle_index = len(list_of_dicts) // 2 - 1
            # Ensure the middle_index points to a "user" role entry if the list is not strictly alternating roles
            while list_of_dicts[middle_index]["role"] != "user":
                middle_index += 1  # Adjust index to find the next "user" entry
            del list_of_dicts[middle_index]
        else:
            # If less than 5, proceed with reducing content of the longest "user" entry
            list_of_dicts = reduce_content(list_of_dicts, word_limit)
    
    return list_of_dicts


    # def choose_random_model(self):
    #     model_names = list(self.models_json.keys())
    #     model_name = random.choice(model_names)
    #     model = self.models_json[model_name]
    #     return model

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
