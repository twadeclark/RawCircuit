import random

from content_loaders.scraper import remove_extra_whitespace

def generate_instructions_wrapping_input(topic, comment):
    instructions = ""
    instructions += ""

    # this works well for small models
    instructions += "You are a very " + get_descriptor() + " converstionalist. "
    instructions += "The topic is '" + remove_extra_whitespace(topic) + "'. Keep that topic in mind when writing your Response. "
    instructions += "You will read the Instruction below and summarize it in your own words. "
    instructions += "Your Response to the Instruction will be " + get_length() + ", and it will " + get_metaphor() + ". "
    instructions += "Take some time to organize your thoughts and revise your Response. "
    instructions += "\n"
    instructions += "### Instruction:\n"
    instructions += remove_extra_whitespace(comment) + "\n"
    instructions += "### Response:\n"

    return instructions

def generate_brief_instructions():
    instructions = ""
    instructions += "You are a very " + get_descriptor() + " converstionalist, and your reply will " + get_metaphor()

    return instructions

def generate_instructions():
    instructions = ""

    instructions += "Your role is " + get_profession() + ". "
    instructions += "Your tone will be " + get_descriptor() + ". "
    instructions += "Your reply will " + get_metaphor() + ". "
    instructions += "Your reply is limited to " + get_length() + ". "
    instructions += get_revise_thoughts()
    instructions += "You will reply to the following message: "

        # instructions = "You are a robot who speaks with boops and beeps in every sentence. You are flatulent. You will reply in a love letter."
        # instructions = "You are a 3 year old toddler who barely makes coherent sentences. you do not use emojis."
        # instructions = "You are a caveman. Your reply will be only 3 words long."

    return instructions

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

def get_profession():
    get_profession_list = [
        "politician",
        "poet",
        "teacher",
        "plumber",
        "blacksmith",
        "auctioneer",
        "camp counselor",
        "cowboy",
        "farmer",
        "woodworker",
        "youtuber",
        "degnerate gambler",
        "college professor",
        "lazy bum",
        "young child",
        "conversationalist",
        "environmental activist",
        "social worker",
        "veterinarian",
        "chef",
        "journalist",
        "software engineer",
        "artist",
        "human rights lawyer",
        "nurse",
        "musician",
        "architect",
        "biologist",
        "civil rights activist",
        "economist",
        "fashion designer",
        "graphic designer",
        "historian",
        "industrial designer",
        "librarian",
        "mathematician",
        "nutritionist",
        "pharmacist",
        "physicist",
        "psychologist",
        "religious leader",
        "school principal",
        "social media influencer",
        "urban planner",
        "veterinarian technician",
        "wildlife conservationist",
        "athlete",
        "baker",
        "carpenter",
        "dentist",
        "electrical engineer",
        "filmmaker",
        "gardener",
        "human resources manager",
        "interpreter",
        "judge",
        "kindergarten teacher",
        "mechanic",
        "nurse practitioner",
        "optometrist",
        "physiotherapist",
        "quality assurance analyst",
        "research scientist",
        "sailor",
        "translator",
        "video game developer",
        "writer",
        "zoologist",
        "accountant",
        "banker",
        "robot",
        "astronaut",
        "astronomer",
        "chemist",
    ]
    return random.choice(get_profession_list)
