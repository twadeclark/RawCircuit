from contributors.openai_interface import OpenAIInterface

class AIManager:
    def __init__(self):
        # Initialize with available AI providers
        self.providers = {
            'OpenAI_interface': OpenAIInterface()
        }

    def generate_comment(self, provider_name, incoming_text, instructions):
        provider = self.providers.get(provider_name)
        if provider:
            return provider.generate_comment(incoming_text, instructions)
        else:
            raise ValueError("AI provider not found")

    def get_summary(self, provider_name, article_text):
        provider = self.providers.get(provider_name)
        if provider:
            return provider.generate_summary(article_text)
        else:
            raise ValueError("AI provider not found")
