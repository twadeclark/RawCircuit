import json
import random
import requests
from transformers import AutoTokenizer
from contributors.abstract_ai_unit import AbstractAIUnit


class HuggingFaceInterface(AbstractAIUnit):
    def __init__(self, config):
        self.api_key = config["api_key"]
        self.base_url = config["base_url"]

    def fetch_inference(self, model, formatted_messages, is_summary):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        this_api_endpoint = self.base_url + model['name']
        formatted_messages_as_string = None

        if is_summary:
            max_new_tokens = 250
            temperature = 0.7
            repetition_penalty = 1.0
        else:
            max_new_tokens = random.randint(1, 10) * 25
            temperature = random.uniform(0.0, 2.0)
            repetition_penalty = random.uniform(0.0, 2.0)

        if isinstance(formatted_messages, str):
            formatted_messages_as_string = formatted_messages
        else:
            kwargs = {}
            kwargs["token"] = self.api_key
            tokenizer = AutoTokenizer.from_pretrained(model["name"], **kwargs)
            formatted_messages_as_string = tokenizer.apply_chat_template(formatted_messages, tokenize=False, add_generation_prompt=True)

        temperature_as_string = "{:.1f}".format(temperature)
        repetition_penalty_as_string = "{:.1f}".format(repetition_penalty)

        flavors = f" \t max_new_tokens: {max_new_tokens}, \t temperature: {temperature_as_string}, \t repetition_penalty: {repetition_penalty_as_string}"

        # print("\n\n",formatted_messages_with_chat_template_applied.strip)

        q = {
            "inputs": formatted_messages_as_string,
            "parameters": { 
                            "max_new_tokens"        : max_new_tokens,
                            "temperature"           : temperature,
                            "repetition_penalty"    : repetition_penalty,
                            "max_time"              : 120,
                            "do_sample"             : True,
                            "return_full_text"      : False
                            },
            "options":    { "wait_for_model": True,
                            "use_cache": False,
                            "stream": True
                            }
            }


        print("    flavors: ", flavors)

        def query(payload):
            response = requests.post(this_api_endpoint, headers=headers, json=payload, timeout=120)
            all_chunks = ""

            for chunk in response.iter_content(decode_unicode=True):
                print(chunk, end="")
                all_chunks += chunk

            print()
            response.close()
            return json.loads(all_chunks)

        data = query(q)

        target_keys = ['error', 'errors', 'warning', 'warnings', 'generated_text', 'summary_text']
        results = self.find_keys(data, target_keys)

        # big problems:
        if results.get('error'):
            print("Error: ", results['error'])

        if results.get('errors'):
            print("Errors: ", results['errors'])

        # small problems:
        if results.get('warning'):
            print("Warning: ", results['warning'])

        if results.get('warnings'):
            print("Warnings: ", results['warnings'])

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
