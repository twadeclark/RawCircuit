from openai import OpenAI
from contributors.abstract_ai_unit import AbstractAIUnit

class LocalOpenAIInterface(AbstractAIUnit):
    def __init__(self):
        self.model = None
        self.client = None

    def fetch_inference(self, model, prompt):
        client = OpenAI(base_url=model["api_url"], api_key=model["api_key"])

        stream = client.completions.create(
            prompt=prompt,
            max_tokens=800,
            n=1,
            temperature=model["temperature_summary"],
            presence_penalty=0.1,
            model=model["model_name"],
            stream=True,
        )

        content = ""
        for chunk in stream:
            if not chunk.choices or chunk.choices[0].text is None:
                continue

            # if "###" in chunk.choices[0].text:
            #     break

            content += chunk.choices[0].text
            print(chunk.choices[0].text, end="")

        stream.close()

        return content

    def _truncate_text(self, article_text):
        max_tokens = self.model["max_tokens"]
        naive_word_estimate = max_tokens / 2
        article_text = article_text.split(" ")
        article_text = article_text[:int(naive_word_estimate)]
        article_text = " ".join(article_text)

        return article_text


    # def generate_new_comment_from_summary_and_previous_comment(self, instructions, summary_text, previous_comment):
    #     pass

    # def fetch_inference_comment_with_fully_formatted_prompt(self, prompt):
    #     pass

    # def prepare_model(self, model):
    #     self.model = model
    #     self.client = OpenAI(base_url=self.model["api_url"], api_key=self.model["api_key"])

    # def fetch_inference_summary(self, article_text, model):
    #     client = OpenAI(base_url=model["api_url"], api_key=model["api_key"])
    #     stream = self.client.completions.create(
    #         prompt="You will read this article, and write a short summary in your own words.\n\n" + self._truncate_text(article_text) + "\n### Response:\n",
    #         max_tokens=800,
    #         n=1,
    #         temperature=self.model["temperature_summary"],
    #         presence_penalty=0.1,
    #         model=self.model["model_name"],
    #         stream=True,
    #     )
        
    #     content = ""
    #     for chunk in stream:
    #         if not chunk.choices or chunk.choices[0].text is None:
    #             continue

    #         # if "###" in chunk.choices[0].text:
    #         #     break

    #         content += chunk.choices[0].text
    #         print(chunk.choices[0].text, end="")

    #     stream.close()

    #     return content

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
