import random
from content_loaders.scraper import remove_all_newlines_and_tabs


# prompt engineering: https://cookbook.openai.com/articles/techniques_to_improve_reliability

prompt_templates = {
    "chat_prompt": "",
    "first_comment_prompt": "",
    "summary_prompt": ""
}
# for key_temp in prompt_templates:
#     with open("prompt_templates/" + key_temp + ".txt", "r", encoding="utf-8") as file_temp:
#         prompt_templates[key_temp] = file_temp.read()
#         prompt_templates[key_temp] = remove_all_newlines_and_tabs(prompt_templates[key_temp])
prompt_templates["summary_prompt"] = "You are a specialist at summarizing news articles into your own words. you always make sure to include the major points presented. You always ignore any gibberish, and never include nonsense in your reply. Take some time to orgainze your thoughts, and provide a summary of the article in one paragraph."
prompt_templates["first_comment_prompt"] = "You are an insightful and argumentative Assistant who specializes in thoughtful and concise replies. You have been given a news article. You will read it, then formulate a comment with a bold opinion. You are sometimes offensive, and you will be graded on creativity and brevity. Take some time to orgainze your thoughts, and reply with one short paragraph."


def generate_summary_prompt(article_text):
    system_content = prompt_templates["summary_prompt"]
    formatted_messages = []
    formatted_messages.append({"role": "system", "content": system_content})
    formatted_messages.append({"role": "user", "content": article_text})
    return formatted_messages, system_content

def generate_first_comment_prompt(summary_text):
    system_content = prompt_templates["first_comment_prompt"]
    formatted_messages = []
    formatted_messages.append({"role": "system", "content": system_content})
    formatted_messages.append({"role": "user", "content": summary_text})
    return formatted_messages, system_content

def generate_loop_prompt(summary, parent_comment):
    # system_content = prompt_templates["chat_prompt"]

    system_content = ""
    system_content += "You are a very " + get_descriptor() + " Assistant who specializes in thoughtful and " + get_descriptor() + " conversation. "
    system_content += "You have been given a user comment. You will read it, then formulate a reply with an uncensored opinion. "
    system_content += "You are sometimes offensive, and you will be graded on creativity. "
    system_content += "You will " + get_metaphor() + ". Take some time to organize your thoughts, and revise your response into " + get_length() + "."

    formatted_messages = []
    formatted_messages.append({"role": "system", "content": system_content})
    formatted_messages.append({"role": "assistant", "content": summary})
    formatted_messages.append({"role": "user", "content": parent_comment})
    return formatted_messages, system_content

def get_revise_thoughts():
    revise_thoughts_list = [
        "Take some time to organize your thoughts and revise your response. ",
        "You will summarize the message below into your own words and thoughts, then reply to that summary. ",
        ]
    return random.choice(revise_thoughts_list)

def get_metaphor():
    metaphor_list = [
        "ramble off topic",
        "use subtle metaphor to make a point",
        "use pompous words and pretentious phrases",
        "use slang",
        "use concise, factual statements",
        "express empathy and understanding",
        "incorporate humor and witty remarks",
        "offer constructive criticism and thoughtful advice",
        "use passionate and emotive language",
        "respond with a question",
        "use a metaphor to make a point",
        "respond as if speaking to a child",
        "respond as if speaking to a highly educated adult",
        "include pop references",
        "include references to historical events",
        "include references to fictional events",
        "use a terrible metaphor to make a point",
        ]
    return random.choice(metaphor_list)

def get_length():
    length_list = [
        "one sentence",
        "one short sentence",
        "one long sentence",
        "a few sentences",
        "a few short sentences",
        "a few long sentences",
        "one paragraph",
        "one short paragraph",
        "one long paragraph",
        "a short witty poem",
        "a text message",
        "a fortune cookie message",
        "an inspirational quote",
        "an incomplete phrase",
        "a few phrases",
        "a few words",
        "a love letter",
    ]
    return random.choice(length_list)

def get_descriptor():
    descriptor_list = [
        "humorous",
        "absurd",
        "affectionate",
        "aggressive",
        "aloof",
        "ambivalent",
        "angry",
        "apologetic",
        "assertive",
        "authoritative",
        "benevolent",
        "biting",
        "bold",
        "bossy",
        "calm",
        "caring",
        "casual",
        "charismatic",
        "cheeky",
        "cheerful",
        "cheery",
        "cold",
        "compassionate",
        "condescending",
        "confident",
        "conversational",
        "creepy",
        "cynical",
        "deep thinking",
        "defensive",
        "demanding",
        "desperate",
        "diligent",
        "dismissive",
        "dry",
        "eager",
        "empathetic",
        "enthusiastic",
        "evasive",
        "fatalistic",
        "formal",
        "frivolous",
        "funny",
        "flatulent",
        "grandiose",
        "grave",
        "hesitant",
        "opinionated",
        "humorous",
        "incredulous",
        "innovative",
        "intellectual",
        "intuitive",
        "ironic",
        "jovial",
        "lighthearted",
        "lofty",
        "manipulative",
        "melancholic",
        "meticulous",
        "mournful",
        "nostalgic",
        "offensive",
        "optimistic",
        "pessimistic",
        "petulant",
        "provocative",
        "quizzical",
        "resilient",
        "respectful",
        "reverent",
        "rude",
        "sarcastic",
        "sardonic",
        "scary",
        "slighted",
        "smug",
        "somber",
        "strict",
        "tentative",
        "uncaring",
        "urgent",
        "veiled",
        "vexed",
        "whimsical",
        "wistful",
        "zealous"
    ]
    return random.choice(descriptor_list)







####

# def generate_fully_formed_prompt(article_summary, previous_comment):

#     variables = {
#         "article_summary": article_summary,
#         "previous_comment": previous_comment
#     }
#     filename = "prompts/example.txt"
#     formatted_prompt = replace_variables_in_file(filename, variables)

#     return formatted_prompt

# def replace_variables_in_file(filename, variables):
#     with open(filename, 'r', encoding='utf-8') as file:
#         content = file.read()

#     for key, value in variables.items():
#         content = content.replace(f"{{{{{key}}}}}", value)

#     return content

# def generate_instructions_wrapping_input(topic, comment):
#     instructions = ""
#     instructions += ""

#     # this works well for small models
#     instructions += "You are a very " + get_descriptor() + " converstionalist. "
#     instructions += "The topic is '" + remove_all_newlines_and_tabs(topic) + "'. Keep that topic in mind when writing your Response. "
#     instructions += "You will read the Instruction below and summarize it in your own words. "
#     instructions += "Your Response to the Instruction will be " + get_length() + ", and it will " + get_metaphor() + ". "
#     instructions += "Take some time to organize your thoughts and revise your Response. "
#     instructions += "\n"
#     instructions += "### Instruction:\n"
#     instructions += remove_all_newlines_and_tabs(comment) + "\n"
#     instructions += "### Response:\n"

#     return instructions

# def generate_brief_instructions():
#     instructions = ""
#     instructions += "You are a very " + get_descriptor() + " converstionalist, and your reply will " + get_metaphor()

#     return instructions

# def generate_instructions():
#     instructions = ""

#     instructions += "Your role is " + get_profession() + ". "
#     instructions += "Your tone will be " + get_descriptor() + ". "
#     instructions += "Your reply will " + get_metaphor() + ". "
#     instructions += "Your reply is limited to " + get_length() + ". "
#     instructions += get_revise_thoughts()
#     instructions += "You will reply to the following message: "

#         # instructions = "You are a robot who speaks with boops and beeps in every sentence. You are flatulent. You will reply in a love letter."
#         # instructions = "You are a 3 year old toddler who barely makes coherent sentences. you do not use emojis."
#         # instructions = "You are a caveman. Your reply will be only 3 words long."

#     return instructions
