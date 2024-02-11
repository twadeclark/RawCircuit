import json
import random
import requests
from contributors.abstract_ai_unit import AbstractAIUnit

class GenericApiInterface(AbstractAIUnit):
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

        # flavors - https://huggingface.co/docs/api-inference/detailed_parameters#text-generation-task
        max_new_tokens = random.randint(1, 10) * 25 # 0 - 250
        temperature = random.uniform(0.0, 100.0) # range 0.0 - 100.0, Default: 1.0
        repetition_penalty = random.uniform(0.0, 100.0) # range 0.0 - 100.0, Default: None

        max_new_tokens_as_string = str(max_new_tokens)
        temperature_as_string = "{:.1f}".format(temperature)
        repetition_penalty_as_string = "{:.1f}".format(repetition_penalty)

        flavors = f" \t max_new_tokens: {max_new_tokens_as_string}, \t temperature: {temperature_as_string}, \t repetition_penalty: {repetition_penalty_as_string}"
        print(flavors)

        data = query(
            {
                "inputs": formatted_messages,
                "parameters": {"max_time": 120,
                               "do_sample": True,
                               "max_new_tokens": max_new_tokens,
                               "temperature": temperature,
                               "repetition_penalty": repetition_penalty,
                               "return_full_text": False,
                               },
                "options": {"wait_for_model": True,
                            "use_cache": False}
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
