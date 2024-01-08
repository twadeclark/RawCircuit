from openai import OpenAI
from contributors.abstract_provider import AbstractProvider

class OpenAI_interface(AbstractProvider):
    def generate_comment(self, article_text, instructions):
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed") # TODO: pass this in as a parameter

        # generate summary here
        summary_instructions = """You are a specialist in summarizing. 
        You will provide an excellent short summary of the following article. 
        You will use your own words to summarize the article. 
        You will not copy any text from the article. You will not plagiarize.
        """

        messages = [
            {"role": "system", "content": summary_instructions},
            {"role": "user", "content": article_text},
        ]

        summary_response = client.chat.completions.create(
            model="local-model", # this field is currently unused
            messages=messages,
            temperature=0.7,
            stream=False,
        )

        if summary_response is not None:
            try:
                summary = summary_response.choices[0].message.content
            except Exception as e:
                print("Summary - Error (response.choices[0].message.content):", e)
                return None
        else:
            print("Summary - No response or an error occurred")
            return None
        
        print("\nSummary:")
        print(summary)


        # generate comment here
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": summary},
        ]

        response = client.chat.completions.create(
            model="local-model", # this field is currently unused
            messages=messages,
            temperature=0.7,
            stream=False,
        )

        if response is not None:
            try:
                content = response.choices[0].message.content
                return content
            except Exception as e:
                print("Error (response.choices[0].message.content):", e)
                return None
        else:
            print("No response or an error occurred")
            return None

