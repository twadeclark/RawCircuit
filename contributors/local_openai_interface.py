from openai import OpenAI
from content_loaders.scraper import make_polite_name
from contributors.abstract_ai_unit import AbstractAIUnit

class LocalOpenAIInterface(AbstractAIUnit):
    def __init__(self, config):
        self.config = config
        self.model = None
        self.client = None
        self.base_url = self.config["base_url"]
        self.api_key = self.config["api_key"]

    def fetch_inference(self, model, formatted_messages):
        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        content = ""

        stream = client.chat.completions.create(
            messages=formatted_messages,
            model=model["model_name"],
            stream=True,
            frequency_penalty=1.1,
            presence_penalty=1.1,
        )

        chunk = None

        for chunk in stream:
            if not chunk.choices or chunk.choices[0].delta.content is None:
                continue

            print(chunk.choices[0].delta.content, end="")

            if '###' in content or '```' in content: # early stop
                break

            content += chunk.choices[0].delta.content

        stream.close()
        client.close()

        print("\n")

        # chunk.model contains the full path of the model used for the completion
        # C:\Users\twade\.cache\lm-studio\models\TheBloke\openchat-3.5-0106-GGUF\openchat-3.5-0106.Q5_K_M.gguf
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
                    model_name = make_polite_name(model_name)
                    model["polite_name"] = model_name.strip()

        return content


        #### deprecated as of 4 jan 2024
        #### https://platform.openai.com/docs/api-reference/completions
        # stream = client.completions.create(
        #     prompt=prompt,
        #     max_tokens=800,
        #     # temperature=model["temperature_message"],
        #     presence_penalty=0.1,
        #     model=model["model_name"],
        #     stream=True,
        # )
