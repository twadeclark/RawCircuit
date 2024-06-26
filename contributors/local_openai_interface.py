import time
import logging
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from contributors.abstract_ai_unit import AbstractAIUnit

from log_config import setup_logging
setup_logging()

class LocalOpenAIInterface(AbstractAIUnit):
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.base_url = config["base_url"]
        self.api_key = config["api_key"]

    def fetch_inference(self, model, formatted_messages, temperature):
        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        content = ""

        max_tokens = 250

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

        start_time = time.time()
        first_chunk_time = None
        token_count = 0

        for chunk in stream:
            token_count += 1
            if first_chunk_time is None:
                first_chunk_time = time.time()

            if not chunk.choices or not chunk.choices[0].delta.content:
                continue

            print(chunk.choices[0].delta.content, end="")

            # if '###' in content or '```' in content: # early stop
            #     break

            content += chunk.choices[0].delta.content

        stream.close()
        client.close()

        end_time = time.time()

        print()
        self.logger.info(content)

        time_to_first_token = first_chunk_time - start_time
        tokens_per_second = token_count / (end_time - first_chunk_time)

        max_tokens_as_string = str(max_tokens)
        temperature_as_string = "{:.2f}".format(temperature)
        flavors = f" \t max_tokens: {max_tokens_as_string}, \t temperature: {temperature_as_string}, \t time_to_first_token: {time_to_first_token:.3f}, \t tokens_per_second: {tokens_per_second:.2f}"
        self.logger.info(flavors)


        # chunk.model contains the full path of the model used for the completion
        # C:\Users\twade\.cache\lm-studio\models\TheBloke\openchat-3.5-0106-GGUF\openchat-3.5-0106.Q5_K_M.gguf
        model_name = None
        if chunk.model is not None and isinstance(chunk.model, str):
            parts = chunk.model.split("\\")
            if parts:
                if len(parts) >= 3:
                    model["name"] = f"{parts[-3]}/{parts[-1]}"
                    model_name = parts[-1]
                    model_name = model_name.strip()
                    if model_name.lower().endswith(".gguf"):
                        model_name = model_name[:-5]

        return content, flavors
