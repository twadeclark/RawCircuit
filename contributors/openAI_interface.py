from openai import OpenAI
from contributors.abstract_provider import AbstractProvider

class OpenAI_interface(AbstractProvider):
    def generate_comment(self, article, instructions):
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed") # TODO: pass this in as a parameter

        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": article},
        ]

        response = client.chat.completions.create(
            model="local-model", # this field is currently unused
            messages=messages,
            temperature=0.7,
            stream=False,
        )

        # print("raw response:", response)

        if response is not None:
            try:
                content = response.choices[0].message.content
                # print("content:", content)
                return content
            except Exception as e:
                print("Error (response.choices[0].message.content):", e)
                return None
        else:
            print("No response or an error occurred")
            return None

