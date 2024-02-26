import json
import time
import requests
try:
    from transformers import AutoTokenizer
except ImportError:
    AutoTokenizer = None
from contributors.abstract_ai_unit import AbstractAIUnit
# from prompt_generator.apply_chat_template_cheater import ApplyChatTemplateCheater


class HuggingFaceInterface(AbstractAIUnit):
    def __init__(self, config):
        self.api_key = config["api_key"]
        self.base_url = config["base_url"]

    def fetch_inference(self, model, formatted_messages, temperature):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        this_api_endpoint = self.base_url + model['name']
        formatted_messages_as_string = None
        max_new_tokens = 250

        if temperature == 0.0:
            temperature = 0.001

        if isinstance(formatted_messages, str):
            formatted_messages_as_string = formatted_messages
        else:
            kwargs = {}
            kwargs["token"] = self.api_key
            tokenizer = AutoTokenizer.from_pretrained(model["name"], **kwargs)
            formatted_messages_as_string = tokenizer.apply_chat_template(formatted_messages, tokenize=False, add_generation_prompt=True)

        print(f"formatted_messages_as_string={formatted_messages_as_string}")

        payload = {
            "inputs": formatted_messages_as_string,
            "parameters": { 
                            "max_new_tokens"        : max_new_tokens,
                            "temperature"           : temperature,
                            "max_time"              : 120,
                            "do_sample"             : True,
                            "return_full_text"      : False
                            },
            "options":    { "wait_for_model": True,
                            "use_cache": False,
                            "stream": True
                            }
            }

        start_time = time.time()
        first_chunk_time = None
        token_count = 0
        end_time = None
        all_chunks = ""

        response = requests.post(this_api_endpoint, headers=headers, json=payload, timeout=120)

        for chunk in response.iter_content(decode_unicode=True):
            token_count += 1
            if first_chunk_time is None:
                first_chunk_time = time.time()

            print(chunk, end="")
            all_chunks += chunk

        response.close()
        data = json.loads(all_chunks)
        end_time = time.time()

        print()

        time_to_first_token = first_chunk_time - start_time
        tokens_per_second = token_count / (end_time - start_time)


        print(f"        total time: {end_time - start_time:.3f}")


        max_tokens_as_string = str(max_new_tokens)
        temperature_as_string = "{:.1f}".format(temperature)
        flavors = f" \t max_tokens: {max_tokens_as_string}, \t temperature: {temperature_as_string}, \t time_to_first_token: {time_to_first_token:.3f}, \t tokens_per_second: {tokens_per_second:.2f}"
        print(flavors)

        target_keys = ['error', 'errors', 'warning', 'warnings', 'generated_text', 'summary_text']
        results = self.find_keys(data, target_keys)

        # big problems:
        if results.get('error'):
            print("Error: ", results['error'])
            raise SystemError(f"Error: {results['error']}")

        # small problems:
        if results.get('warning'):
            print("Warning: ", results['warning'])

        # success stories:
        response = None
        if results.get('generated_text'):
            response = results['generated_text']

        if results.get('summary_text'):
            response = results['summary_text']

        return response, flavors


    def find_keys(self, json_input, target_keys):
        results = {}

        def _find_keys_recursive(json_fragment):
            if isinstance(json_fragment, dict):
                for key, value in json_fragment.items():
                    if key in target_keys:
                        results[key] = value
                    _find_keys_recursive(value)
            elif isinstance(json_fragment, list):
                for item in json_fragment:
                    _find_keys_recursive(item)

        _find_keys_recursive(json_input)
        return results
