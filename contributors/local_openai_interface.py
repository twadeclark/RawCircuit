from openai import OpenAI
from contributors.abstract_ai_unit import AbstractAIUnit

class LocalOpenAIInterface(AbstractAIUnit):
    def __init__(self):
        self.model = None
        self.client = None

    def fetch_inference(self, model, formatted_messages):
        client = OpenAI(base_url=model["api_url"], api_key=model["api_key"])
        content = ""

        stream = client.chat.completions.create(
            messages=formatted_messages,
            model=model["model_name"],
            stream=True,
            frequency_penalty=1.1,
            # max_tokens=100,
            presence_penalty=1.1,
            # temperature=model["temperature_message"],
        )

        for chunk in stream:
            if not chunk.choices or chunk.choices[0].delta.content is None:
                continue

            content += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end="")

        stream.close()
        client.close()

        print("\n")

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
