import json
import random
from content_loaders.scraper import make_polite_name
from contributors.hugging_face_interface import HuggingFaceInterface
from contributors.local_openai_interface import LocalOpenAIInterface

class AIManager:
    def __init__(self, config):
        self.config = config
        self.interface_list = {
            'LocalOpenAIInterface': LocalOpenAIInterface(config["LocalOpenAIInterface"]),
            'HuggingFaceInterface': HuggingFaceInterface(config["HuggingFace"])
        }

        with open('models.json', 'r', encoding='utf-8') as file:
            self.models_json = json.load(file)

    def return_model_by_name(self, model_name):
        if model_name is None or len(model_name) == 0:
            model_name = self._choose_random_model_name()
        model = self.models_json[model_name]
        model["model_name"] = model_name

        polite_name = make_polite_name(model_name)
        model["polite_name"] = polite_name

        return model

    def fetch_inference(self, model, formatted_messages):
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

        response = truncate_from_marker(response, "```")
        response = truncate_from_marker(response, "###")

        return response.strip()


    def _choose_random_model_name(self):
        model_names = list(self.models_json.keys())
        model_name = random.choice(model_names)
        return model_name


def truncate_from_marker(input_string, marker="```"):
    marker_index = input_string.find(marker)

    if marker_index == -1:
        return input_string

    truncated_string = input_string[:marker_index]
    removed_text = input_string[marker_index:]
    print(f"\n    Removed text for {marker} from here -->{removed_text}<-- to here.\n\n")

    return truncated_string

def calculate_word_count(list_of_dicts):
    combined_string = " ".join(item["content"] for item in list_of_dicts)
    return len(combined_string.split())

def reduce_content(list_of_dicts, word_limit):
    while calculate_word_count(list_of_dicts) > word_limit:
        longest_user_content = None
        longest_user_index = -1
        for i, item in enumerate(list_of_dicts):
            if item["role"] == "user":
                if longest_user_content is None or len(item["content"].split()) > len(longest_user_content.split()):
                    longest_user_content = item["content"]
                    longest_user_index = i

        if longest_user_content:
            words = longest_user_content.split()
            one_third_length = len(words) // 3
            reduced_content = ' '.join(words[:one_third_length] + words[-one_third_length:])
            list_of_dicts[longest_user_index]["content"] = reduced_content

    return list_of_dicts

def adjust_content_based_on_user_entries(list_of_dicts, word_limit):
    #TODO: https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken

    while calculate_word_count(list_of_dicts) > word_limit:
        user_entries = [item for item in list_of_dicts if item["role"] == "user"]
        user_entries_count = len(user_entries)

        if user_entries_count >= 5:
            middle_index = len(list_of_dicts) // 2 - 1
            while list_of_dicts[middle_index]["role"] != "user":
                middle_index += 1
            del list_of_dicts[middle_index]
        else:
            list_of_dicts = reduce_content(list_of_dicts, word_limit)

    return list_of_dicts
