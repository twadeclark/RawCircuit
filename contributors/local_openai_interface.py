import random
from openai import OpenAI
from content_loaders.scraper import make_polite_name
from contributors.abstract_ai_unit import AbstractAIUnit

class LocalOpenAIInterface(AbstractAIUnit):
    def __init__(self, config):
        self.base_url = config["base_url"]
        self.api_key = config["api_key"]

    def fetch_inference(self, model, formatted_messages):
        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        content = ""

        # flavors
        max_tokens = random.randint(1, 20) * 25
        temperature = random.uniform(0.0, 2.0) # range 0 - 2, Defaults to 1
        frequency_penalty = random.uniform(-2.0, 2.0) # range -2.0 - 2.0, Defaults to 0
        presence_penalty = random.uniform(-2.0, 2.0) # range -2.0 - 2.0, Defaults to 0

        max_tokens_as_string = str(max_tokens)
        temperature_as_string = "{:.1f}".format(temperature)
        frequency_penalty_as_string = "{:.1f}".format(frequency_penalty)
        presence_penalty_as_string = "{:.1f}".format(presence_penalty)

        flavors = f" \t max_tokens: {max_tokens_as_string}, \t temperature: {temperature_as_string}, \t frequency_penalty: {frequency_penalty_as_string}, \t presence_penalty: {presence_penalty_as_string}"
        print(flavors)

        stream = client.chat.completions.create( timeout=6000, # 100 minutes
            messages=formatted_messages,
            model=model["model_name"],
            stream=True,
            max_tokens=max_tokens,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
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
        if model_name is None or len(model_name) == 0:
            model["polite_name"] = make_polite_name(model["model_name"])
        if model_name is None or len(model_name) == 0:
            model_name = model["model_name"]

        return content, flavors


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
