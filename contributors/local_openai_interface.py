from openai import OpenAI
from contributors.abstract_ai_unit import AbstractAIUnit

class LocalOpenAIInterface(AbstractAIUnit):
    def __init__(self, config):
        self.base_url = config["base_url"]
        self.api_key = config["api_key"]

    def fetch_inference(self, model, formatted_messages, temperature):
        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        content = ""
        
        max_tokens = 250
        max_tokens_as_string = str(max_tokens)
        temperature_as_string = "{:.2f}".format(temperature)
        flavors = f" \t max_tokens: {max_tokens_as_string}, \t temperature: {temperature_as_string}"
        print(flavors)

        stream = client.chat.completions.create( timeout=6000, # 100 minutes
            messages=formatted_messages,
            model="LocalLLM",
            stream=True,
            max_tokens=max_tokens,
            temperature=temperature,
            # frequency_penalty=frequency_penalty,
            # presence_penalty=presence_penalty,
        )

        chunk = None

        for chunk in stream:
            if not chunk.choices or not chunk.choices[0].delta.content:
                continue

            print(chunk.choices[0].delta.content, end="")

            # if '###' in content or '```' in content: # early stop
            #     break

            content += chunk.choices[0].delta.content

        stream.close()
        client.close()

        print()

        # chunk.model contains the full path of the model used for the completion
        # C:\Users\twade\.cache\lm-studio\models\TheBloke\openchat-3.5-0106-GGUF\openchat-3.5-0106.Q5_K_M.gguf
        model_name = None
        if chunk.model is not None and isinstance(chunk.model, str):
            parts = chunk.model.split("\\")
            if parts:
                if len(parts) >= 3:
                    model_name = parts[-1]
                    model_name = model_name.strip()
                    if model_name.lower().endswith(".gguf"):
                        model_name = model_name[:-5]
            if model_name:
                model["name"] = model_name

        return content, flavors
