from openai import OpenAI
from contributors.abstract_provider import AbstractProvider

class OpenAIInterface(AbstractProvider):
    def __init__(self):
        self.model = None
        self.client = None

    def prepare_model(self, model):
        self.model = model
        self.client = OpenAI(base_url=self.model["base_url"], api_key=self.model["api_key"])

    def generate_summary(self, article_text):
        summary_response = self.client.completions.create(
            prompt="You will ignore any nonsense in the following text and find the article only. You will then summarize the article in the style of the New Yorker: " + self.truncate_text(article_text),
            max_tokens=800,
            n=1,
            temperature=self.model["temperature_summary"],
            presence_penalty=0.1,
            model=self.model["model_name"],
            stream=False,
        )
        summary = summary_response.choices[0].text
        return summary

    def generate_comment(self, user_content, system_content):
        content_response = self.client.completions.create(
            # prompt="Summarize this text in the style of the New Yorker: " + self.truncate_text(article_text),
            prompt=system_content + self.truncate_text(user_content),
            max_tokens=800,
            n=1,
            temperature=self.model["temperature_message"],
            presence_penalty=0.1,
            model=self.model["model_name"],
            stream=False,
        )
        content = content_response.choices[0].text

        return content

    def truncate_text(self, article_text): #TODO: make this more robust
        max_tokens = self.model["max_tokens"]
        naive_word_estimate = max_tokens / 2

        # limit article_text to naive_word_estimate number of words. words are separated by spaces
        article_text = article_text.split(" ")
        article_text = article_text[:int(naive_word_estimate)]
        article_text = " ".join(article_text)

        return article_text




        # article_split = article_text.split(" ")
        # length_ltd_text = " ".join(article_split[:naive_word_estimate])
        # return length_ltd_text




