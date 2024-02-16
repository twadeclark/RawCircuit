# import random
# from openai import OpenAI
# from content_loaders.scraper import make_polite_name
# import os
from litellm import completion
import litellm
from content_loaders.scraper import get_polite_name
from contributors.abstract_ai_unit import AbstractAIUnit
litellm.set_verbose = True

class LiteLLMInterface(AbstractAIUnit):
    def __init__(self, config):
        self.base_url = config["base_url"]
        self.api_key = config["api_key"]

    def fetch_inference(self, model, formatted_messages):
        flavors = "no flavors available"

        messages = [{ "content": "There's a llama in my garden 😱 What should I do?","role": "user"}]

        model_parameter = f"huggingface/{model['model_name']}"

        response = completion(
            api_key  = self.api_key,
            model    = model_parameter,
            messages = messages,
            api_base = self.base_url,
            stream   = True,
            wait_for_model = True
        )

        print(response)

        content = ""
        chunk = None

        for chunk in response:
            print(chunk)
            content += chunk.choices[0].delta.content


        model_name = None
        if chunk.model is not None and isinstance(chunk.model, str):
            parts = chunk.model.split("\\")
            if parts:
                if len(parts) >= 3:
                    # model_name = parts[-3] + "_" + parts[-1] # include the maker name
                    model_name = parts[-1]
                    model_name = model_name.strip()
                    if model_name.lower().endswith(".gguf"):
                        model_name = model_name[:-5]
                    model_name = get_polite_name(model_name)
                    model["polite_name"] = model_name.strip()
        if not model_name:
            model["polite_name"] = get_polite_name(model["model_name"])
        if not model_name:
            model_name = model["model_name"]

        return content, flavors
