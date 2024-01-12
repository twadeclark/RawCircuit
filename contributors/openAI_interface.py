import re
from openai import OpenAI
import openai
from contributors.abstract_provider import AbstractProvider

class OpenAIInterface(AbstractProvider):
    def generate_summary(self, article_text):
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed") # TODO: pass this in as a parameter
        summary_instructions = """You are an analytical thinker.
        Use reasoning to ensure the summary is concise and accurate.
        Include only information included in the text.
        Summarize the following text into two or three paragrpahs, capturing all key details.
        """

        messages = [
            {"role": "system", "content": summary_instructions},
            {"role": "user", "content": article_text},
        ]

        summary_response = client.chat.completions.create(
            model="local-model", # TODO: this field is currently unused for local, pass in as a parameter
            messages=messages,
            temperature=0.1,
            stream=False,
        )

        if summary_response:
            try:
                summary = summary_response.choices[0].message.content

                # TODO: move this simple clean up to utility file
                summary = re.sub(r"\[.*\]", "", summary).strip()
                summary = re.sub(r"[\n\r]", " ", summary)

                print("\nSummary:")
                print(summary)
                return summary
            except (IndexError, AttributeError, TypeError) as e:
                print("Summary - Error (response.choices[0].message.content):", e)
        else:
            print("Summary - No response or an error occurred")
        return None

    def generate_comment(self, incoming_text, instructions):
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed") # TODO: pass this in as a parameter

        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": incoming_text},
        ]

        response = client.chat.completions.create(
            model="local-model", # TODO: this field is currently unused for local, pass in as a parameter
            messages=messages,
            temperature=2.0,
            stream=False,
        )

        if response is not None:
            try:
                content = response.choices[0].message.content
                return content
            except (openai.OpenAIError, IndexError) as e:
                print("Error (response.choices[0].message.content):", e)
                return None
        else:
            print("No response or an error occurred")
            return None
