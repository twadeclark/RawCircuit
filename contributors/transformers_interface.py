from transformers import pipeline
# from contributors.abstract_ai_unit import AbstractAIUnit

# class GenericApiInterface(AbstractAIUnit):
#     def __init__(self, config):
#         self.api_key = config["api_key"]
#         self.base_url = config["base_url"]

    # def fetch_inference(self, model, formatted_messages):
    #     response = model + ": " + formatted_messages
    #     return response


def fetch_inference(model_name, messages_list):
    # Ensure the messages_list contains three strings as expected
    if not isinstance(messages_list, list) or len(messages_list) != 3:
        raise ValueError("messages_list must be a list of three strings.")
    
    # Concatenate the messages into a single input string
    input_text = " ".join(messages_list)
    
    # Initialize the pipeline with the specified model
    # This example assumes a text generation task. Adjust the task if necessary.
    text_generator = pipeline("text-generation", model=model_name)
    
    # Generate a response using the model
    # Adjust generation parameters as needed (e.g., max_length, num_return_sequences)
    response = text_generator(input_text, max_length=50, num_return_sequences=1)
    
    # Extract the generated text and return it
    # The response structure can vary, so adjust indexing as needed
    generated_text = response[0]['generated_text']
    
    return generated_text

# Example usage
model_name = "openai-community/gpt2"  # Example model, replace with the model of your choice
messages_list = [
    "System message: The model generates responses based on input.",
    "Assistant message: How can I assist you today?",
    "User message: What is the weather like today?"
]

# Fetch the model's inference
response = fetch_inference(model_name, messages_list)
print(response)
