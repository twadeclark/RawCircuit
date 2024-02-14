import json
import re
# from content_loaders.scraper import make_polite_name
from contributors.hugging_face_interface import HuggingFaceInterface
from contributors.litellm_interface import LiteLLMInterface
from contributors.local_openai_interface import LocalOpenAIInterface
from contributors.transformers_interface import TransformersInterface

class AIManager:
    def __init__(self, config):
        self.config = config
        self.interface_list = {
            'LocalOpenAIInterface': LocalOpenAIInterface(config["LocalOpenAIInterface"]),
            'LiteLLMInterface': LiteLLMInterface(config["LiteLLMInterface"]),
            'HuggingFaceInterface': HuggingFaceInterface(config["HuggingFace"]),
            'TransformersInterface': TransformersInterface(config["TransformersInterface"]),
            # 'GenericApiInterface': GenericApiInterface(config["GenericApiInterface"]),
        }

    def fetch_inference(self, model, formatted_messages):
        interface = self.interface_list.get(model["interface"])
        word_limit = model["max_tokens"] // 2
        formatted_messages = _truncate_user_messages_if_needed(formatted_messages, word_limit)

        # let's go!
        response, flavors = interface.fetch_inference(model, formatted_messages)

        # remove the prompt from the response
        if response is not None and len(response) > 0:
            prompt_length = len(formatted_messages)
            if response[:prompt_length] == formatted_messages:
                response = response[prompt_length:]
            response = response.strip()

        # # clean up the response if we want, but it's more fun to see the raw output
        # response = _truncate_from_marker(response, "```")
        # response = _truncate_from_marker(response, "###")
        # response = _remove_end_repetitions(response)

        return response, flavors


def _truncate_from_marker(input_string, marker="###"):
    marker_index = input_string.find(marker)

    if marker_index == -1:
        return input_string

    truncated_string = input_string[:marker_index]
    removed_text = input_string[marker_index:]
    print(f"\n    Removed text for {marker} from here -->{removed_text}<-- to here.\n\n")

    return truncated_string

def _calculate_word_count(list_of_dicts):
    combined_string = " ".join(item["content"] for item in list_of_dicts)
    return len(combined_string.split())

def _reduce_content(list_of_dicts, word_limit):
    while _calculate_word_count(list_of_dicts) > word_limit:
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

def _truncate_user_messages_if_needed(list_of_dicts, word_limit):
    #TODO: https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken

    while _calculate_word_count(list_of_dicts) > word_limit:
        user_entries = [item for item in list_of_dicts if item["role"] == "user"]
        user_entries_count = len(user_entries)

        if user_entries_count >= 5:
            middle_index = len(list_of_dicts) // 2 - 1
            while list_of_dicts[middle_index]["role"] != "user":
                middle_index += 1
            del list_of_dicts[middle_index]
        else:
            list_of_dicts = _reduce_content(list_of_dicts, word_limit)

    return list_of_dicts

def _remove_end_repetitions(text): # sometimes models with wild settings get stuck in a loop and repeat the same word or punctuation over and over
    # catch repeated words at the end of text, possibly followed by punctuation and spaces. Also catches repeated punctuation or characters.
    pattern = re.compile(r'(\b(\w+)[,.!?\s]*)(?:\2[,.!?\s]*)+$|([,.!?])\3+$')

    def replace_func(match):
        if match.group(2):  # Word repetitions
            return match.group(1)
        else:  # Character repetitions
            return match.group(3)

    cleaned_text = pattern.sub(replace_func, text.strip())

    return cleaned_text
