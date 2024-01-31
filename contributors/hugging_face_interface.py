import requests
from contributors.abstract_ai_unit import AbstractAIUnit
from instruction_generator import get_metaphor

class HuggingFaceInterface(AbstractAIUnit):
    def __init__(self):
        self.model = None

    def prepare_model(self, model):
        self.model = model





    def generate_comment_preformatted_message_streaming(self, message_text):
        API_TOKEN = self.model["api_key"]
        API_URL = self.model["api_url"]
        headers = {"Authorization": f"Bearer {API_TOKEN}"}

        inputs = message_text

        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload, timeout=120) # Add timeout argument
            return response.json()

        data = query(
            {
                "inputs": inputs,
                "parameters": {
                    "do_sample": False,
                    "return_full_text": False
                },
                "options": {"wait_for_model": True}
            }
        )

        print(data)
        generated_text = data[0]["generated_text"]
        # truncate generated_text from the first ###
        generated_text = generated_text.split("###")[0]

        print("    previous_comment: ", message_text)
        print("    generated_text  : ", generated_text)

        return generated_text

    def generate_summary(self, article_text):
        API_TOKEN = self.model["api_key"]
        API_URL = self.model["api_url"]
        headers = {"Authorization": f"Bearer {API_TOKEN}"}

        truncated_text = self._truncate_text(article_text)

        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60) # Add timeout argument
            return response.json()

        data = query(
            {
                "inputs": truncated_text,
                "parameters": {"do_sample": False},
                "options": {"wait_for_model": True}
            }
        )

        summary = data[0]["summary_text"]

        return summary.strip()


    def generate_new_comment_from_summary_and_previous_comment(self, instructions, summary_text, previous_comment):
        API_TOKEN = self.model["api_key"]
        API_URL = self.model["api_url"]
        headers = {"Authorization": f"Bearer {API_TOKEN}"}

        # inputs = f"Article Summary: '{summary_text}.' Desired Style: '{instructions}.' Prompt: '{previous_comment}' Additional Instruction: Keep the response under 50 words. The AI generated response:"
        # inputs = f"Article Summary: {summary_text}. Desired Style: {instructions}. Prompt: {previous_comment} Additional Instruction: Keep the response under 50 words. The AI generated response:"
        # inputs = f"Comment: '{previous_comment}'"

        # inputs = previous_comment + " And then the AI said: '"
        # inputs = "And then the AI said: '"
        # inputs = "You will generate a witty reply to this comment:\n\n " + previous_comment + "\n\n"

        # instructions = "Your reply will " + get_metaphor() + ".\n"


        inputs = "### Comment\n\n" + previous_comment + "\n\n### Counterpoint\n\n" # works on some models
        # inputs = "You will disagree with the following statement.\n" + previous_comment + "\n"



        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload, timeout=120) # Add timeout argument
            return response.json()

        data = query(
            {
                "inputs": inputs,
                "parameters": {
                    "temperature": 1.1,
                    "do_sample": False
                    # "return_full_text": False
                },
                "options": {"wait_for_model": True}
            }
        )

        value = next(iter(data[0].values())) # this should handle the case where the key is anything
        if value == inputs:
            print("    Stuck in a loop.")
            #TODO: handle this better
        print(value)

        generated_text = data[0]["generated_text"]

        print("    inputs          : ", inputs)
        print("    generated_text  : ", generated_text)

        # delete the first line only if it starts with ###
        if generated_text.startswith("###"):
            generated_text = generated_text.split("\n", 1)[1]

        # truncate generated_text from the first ###
        generated_text = generated_text.split("###")[0]

        return generated_text


    def _truncate_text(self, article_text):
        max_tokens = self.model["max_tokens"]
        naive_word_estimate = max_tokens / 2
        article_text = article_text.split(" ")
        article_text = article_text[:int(naive_word_estimate)]
        article_text = " ".join(article_text)

        return article_text
