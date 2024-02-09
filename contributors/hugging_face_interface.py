import json
import random
import requests
from contributors.abstract_ai_unit import AbstractAIUnit

class HuggingFaceInterface(AbstractAIUnit):
    def __init__(self, config):
        self.api_key = config["api_key"]
        self.base_url = config["base_url"]

    def fetch_inference(self, model, formatted_messages):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        this_api_endpoint = self.base_url + model['model_name']

        def query(payload):
            response = requests.post(this_api_endpoint, headers=headers, json=payload, timeout=120, stream=True)
            all_chunks = ""

            for chunk in response.iter_content(chunk_size=1):
                all_chunks += chunk.decode("utf-8")

            response.close()
            return json.loads(all_chunks)

        # flavors
        max_tokens = random.randint(1, 20) * 25
        temperature = random.uniform(0.0, 2.0) # range 0 and 2, Defaults to 1
        frequency_penalty = random.uniform(-2.0, 2.0) # range -2.0 and 2.0, Defaults to 0
        presence_penalty = random.uniform(-2.0, 2.0) # range -2.0 and 2.0, Defaults to 0

        max_tokens_as_string = str(max_tokens)
        temperature_as_string = "{:.1f}".format(temperature)
        frequency_penalty_as_string = "{:.1f}".format(frequency_penalty)
        presence_penalty_as_string = "{:.1f}".format(presence_penalty)

        flavors = f" \t max_tokens: {max_tokens_as_string}, \t temperature: {temperature_as_string}, \t frequency_penalty: {frequency_penalty_as_string}, \t presence_penalty: {presence_penalty_as_string}"
        print(flavors)

        data = query(
            {
                "inputs": formatted_messages,
                "parameters": {"max_length": 500, 
                               "min_length": 100, 
                               "do_sample": False},
                "options": {"wait_for_model": True}
            }
        )

        response = None

        target_keys = ['error', 'errors', 'warning', 'warnings', 'generated_text', 'summary_text']
        results = self.find_keys(data, target_keys)
        print(results)

        # big problems:
        if results.get('error') is not None:
            print("Error: ", results['error'])

        if results.get('errors') is not None:
            print("Errors: ", results['errors'])

        # small problems:
        if results.get('warning') is not None:
            print("Warning: ", results['warning'])

        if results.get('warnings') is not None:
            print("Warnings: ", results['warnings'])

        # success stories:
        if results.get('generated_text') is not None:
            response = results['generated_text']

        if results.get('summary_text') is not None:
            response = results['summary_text']

        return response


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
