import re
from contributors.hugging_face_interface import HuggingFaceInterface
from contributors.local_openai_interface import LocalOpenAIInterface
from contributors.transformers_interface import TransformersInterface

class AIManager:
    def __init__(self, config, db_manager, instruction_generator):
        self.config = config
        self.db_manager = db_manager
        self.interface_list = {
            'HuggingFaceInterface': HuggingFaceInterface(config["HuggingFace"]),
            'LocalOpenAIInterface': LocalOpenAIInterface(config["LocalOpenAIInterface"]),
            'TransformersInterface': TransformersInterface(config["TransformersInterface"]),
            # 'LiteLLMInterface': LiteLLMInterface(config["LiteLLMInterface"]),
            # 'GenericApiInterface': GenericApiInterface(config["GenericApiInterface"]),
        }
        self.instruction_generator = instruction_generator


    def fetch_summary_and_record_model_results(self, model_temp, summary_prompt_temp):
        summary_temp = None
        try:
            summary_temp, _ = self.fetch_inference(model_temp, summary_prompt_temp, 0.0)
            length_of_summary = len(str(summary_temp))
            print(f"    Successful fetch. length_of_summary: {length_of_summary}")
            self.db_manager.update_model_record(model_temp["name"], True, f"length_of_summary: {length_of_summary}")
            return summary_temp, True
        except Exception as e:
            print(f"    Model '{model_temp["name"]}' no worky: ", str(e), "\n")
            self.db_manager.update_model_record(model_temp["name"], False, str(e))
            return summary_temp, False

    def get_summary_and_record_model_results(self, article_to_process):
        summary_instruct = summary_instruct_chat = summary_chat = None
        fetch_success = True

        summary_instruct, fetch_success = self.fetch_summary_and_record_model_results(article_to_process.model, self.instruction_generator.generate_summary_prompt_instruct(article_to_process.shortened_content))
        summary_instruct_chat, fetch_success = self.fetch_summary_and_record_model_results(article_to_process.model, self.instruction_generator.generate_summary_prompt_instruct_chat(article_to_process.shortened_content))
        summary_chat, fetch_success = self.fetch_summary_and_record_model_results(article_to_process.model, self.instruction_generator.generate_summary_prompt_chat(article_to_process.shortened_content))

        summary_dump = ""
        summary_selected = ""

        if summary_instruct:
            summary_dump += f"⚗️ Instruct Template: {summary_instruct} "
            if len(summary_instruct) > len(summary_selected):
                summary_selected = summary_instruct

        if summary_instruct_chat:
            summary_dump += f"⚗️ Instruct Chat Template: {summary_instruct_chat} "
            if len(summary_instruct_chat) > len(summary_selected):
                summary_selected = summary_instruct_chat

        if summary_chat:
            summary_dump += f"⚗️ Chat Template: {summary_chat} "
            if len(summary_chat) > len(summary_selected):
                summary_selected = summary_chat

        if summary_selected:
            summary_selected = summary_selected.replace("\n", " ")
        if summary_dump:
            summary_dump = summary_dump.replace("\n", " ")
        return summary_selected, summary_dump

    def fetch_inference(self, model, formatted_messages, temperature):
        interface = self.interface_list.get(model["interface"])

        # if not isinstance(formatted_messages, str):
        #     word_limit = model["max_tokens"] // 2
        #     formatted_messages = truncate_user_messages_if_needed(formatted_messages, word_limit)

        # let's go!
        response, flavors = interface.fetch_inference(model, formatted_messages, temperature)

        # remove the prompt from the response
        if response:
            prompt_length = len(formatted_messages)
            if response[:prompt_length] == formatted_messages:
                response = response[prompt_length:]
            response = response.strip()

        # # clean up the response if we want, but it's more fun to see the raw output
        # response = _truncate_from_marker(response, "```")
        # response = _truncate_from_marker(response, "###")
        # response = _remove_end_repetitions(response)

        return response, flavors


def _calculate_word_count(list_of_dicts):
    combined_string = " ".join(item["content"] for item in list_of_dicts)
    return len(combined_string.split())

def _reduce_content(list_of_dicts, word_limit):
    while _calculate_word_count(list_of_dicts) > word_limit:
        longest_user_content = None
        longest_user_index = -1
        for i, item in enumerate(list_of_dicts):
            if item["role"] == "user":
                if not longest_user_content or len(item["content"].split()) > len(longest_user_content.split()):
                    longest_user_content = item["content"]
                    longest_user_index = i

        if longest_user_content:
            words = longest_user_content.split()
            one_third_length = len(words) // 3
            reduced_content = ' '.join(words[:one_third_length] + words[-one_third_length:])
            list_of_dicts[longest_user_index]["content"] = reduced_content

    return list_of_dicts

def truncate_user_messages_if_needed(list_of_dicts, word_limit):
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

def _truncate_from_marker(input_string, marker="###"):
    marker_index = input_string.find(marker)

    if marker_index == -1:
        return input_string

    truncated_string = input_string[:marker_index]
    removed_text = input_string[marker_index:]
    print(f"\n    Removed text for {marker} from here -->{removed_text}<-- to here.\n\n")

    return truncated_string

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
