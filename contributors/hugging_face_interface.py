import json
import requests
from contributors.abstract_ai_unit import AbstractAIUnit

class HuggingFaceInterface(AbstractAIUnit):
    def __init__(self):
        pass

    def fetch_inference(self, model, formatted_messages):
        API_TOKEN = model["api_key"]
        API_URL = model["api_url"]
        headers = {"Authorization": f"Bearer {API_TOKEN}"}

        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload, timeout=120, stream=True)
            all_chunks = ""

            for chunk in response.iter_content(chunk_size=1):
                all_chunks += chunk.decode("utf-8")

            response.close()
            return json.loads(all_chunks)

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

        def _find_keys(json_fragment):
            if isinstance(json_fragment, dict):
                for key, value in json_fragment.items():
                    if key in target_keys:
                        results[key] = value
                    _find_keys(value)
            elif isinstance(json_fragment, list):
                for item in json_fragment:
                    _find_keys(item)

        _find_keys(json_input)
        return results
