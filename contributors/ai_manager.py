from contributors.abstract_provider import AbstractProvider
from contributors.openAI_interface import OpenAI_interface
from contributors.local_provider import LocalProvider
from contributors.remote_provider_api1 import RemoteProviderAPI1
from contributors.remote_provider_api2 import RemoteProviderAPI2

class AIManager:
    def __init__(self):
        # Initialize with available AI providers
        self.providers = {
            'OpenAI_interface': OpenAI_interface(),
            'local': LocalProvider(),
            'remote_api1': RemoteProviderAPI1(),
            'remote_api2': RemoteProviderAPI2()
        }

    def get_comment(self, provider_name, article, instructions):
        provider = self.providers.get(provider_name)
        if provider:
            return provider.generate_comment(article, instructions)
        else:
            raise ValueError("AI provider not found")
