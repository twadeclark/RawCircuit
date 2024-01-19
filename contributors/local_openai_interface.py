import re
from openai import OpenAI
import openai
from contributors.abstract_provider import AbstractProvider

class OpenAIInterface(AbstractProvider):
    def __init__(self):
        self.model = None

    def prepare_model(self, model):
        self.model = model

    def generate_summary(self, article_text):
        client = OpenAI(base_url=self.model["base_url"], api_key=self.model["api_key"])

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
            model=self.model["model_name"],
            messages=messages,
            temperature=self.model["temperature_summary"],
            stream=False,
        )

        if summary_response:
            try:
                summary = summary_response.choices[0].message.content
                summary = re.sub(r"\[.*\]", "", summary).strip()
                summary = re.sub(r"[\n\r]", " ", summary)
                return summary
            except (IndexError, AttributeError, TypeError) as e:
                print("Summary - Error (response.choices[0].message.content):", e)
        else:
            print("Summary - No response or an error occurred")
        return None

    def generate_comment(self, user_content, system_content):
        client = OpenAI(base_url=self.model["base_url"], api_key=self.model["api_key"])

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

        response = client.chat.completions.create(
            model=self.model["model_name"],
            messages=messages,
            temperature=self.model["temperature_message"],
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
