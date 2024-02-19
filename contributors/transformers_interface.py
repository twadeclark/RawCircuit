from transformers import pipeline
from contributors.abstract_ai_unit import AbstractAIUnit


class TransformersInterface(AbstractAIUnit):
    def __init__(self, config):
        self.api_key = config["api_key"]
        self.base_url = config["base_url"]

    def fetch_inference(self, model, formatted_messages, temperature):
        model_name = model["name"]
        conversational_pipeline = pipeline(task="conversational", model=model_name)
        conversational_pipeline.model.config.temperature = temperature
        response = conversational_pipeline(formatted_messages)
        generated_text = response.generated_responses[-1]

        return generated_text, "This not flavor town."
