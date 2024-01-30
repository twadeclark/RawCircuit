from openai import OpenAI
from contributors.abstract_ai_unit import AbstractAIUnit

class LocalOpenAIInterface(AbstractAIUnit):
    def __init__(self):
        self.model = None
        self.client = None

    def generate_new_comment_from_summary_and_previous_comment(self, instructions, summary_text, previous_comment):
        pass

    def prepare_model(self, model):
        self.model = model
        self.client = OpenAI(base_url=self.model["api_url"], api_key=self.model["api_key"])

    def generate_summary(self, article_text):
        summary_response = self.client.completions.create(
            prompt="You will read this article, and write a short summary in your own words.\n" + self._truncate_text(article_text) + "\n### Response:\n",
            max_tokens=800,
            n=1,
            temperature=self.model["temperature_summary"],
            presence_penalty=0.1,
            model=self.model["model_name"],
            stream=False,
        )
        summary = summary_response.choices[0].text
        return summary

    def generate_comment_preformatted_message_streaming(self, message_text):
        stream = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": message_text,
                },
            ],
            stream=True,
        )

        content = ""
        for chunk in stream:
            if not chunk.choices or chunk.choices[0].delta.content is None:
                continue

            if "###" in chunk.choices[0].delta.content:
                break

            content += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end="")

        return content

    def _truncate_text(self, article_text):
        max_tokens = self.model["max_tokens"]
        naive_word_estimate = max_tokens / 2
        article_text = article_text.split(" ")
        article_text = article_text[:int(naive_word_estimate)]
        article_text = " ".join(article_text)

        return article_text

    # def generate_comment(self, user_content, system_content):
    #     content_response = self.client.completions.create(
    #         prompt=system_content + self._truncate_text(user_content),
    #         max_tokens=800,
    #         n=1,
    #         temperature=self.model["temperature_message"],
    #         presence_penalty=0.1,
    #         model=self.model["model_name"],
    #         stream=False,
    #     )
    #     content = content_response.choices[0].text

    #     return content

    # def generate_comment_preformatted_message(self, message_text):
    #     content_response = self.client.completions.create(
    #         prompt=message_text,
    #         max_tokens=800,
    #         n=1,
    #         temperature=self.model["temperature_message"],
    #         presence_penalty=0.1,
    #         model=self.model["model_name"],
    #         stream=False,
    #     )
    #     content = content_response.choices[0].text

    #     return content
