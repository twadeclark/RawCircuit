import random


# prompt engineering: https://cookbook.openai.com/articles/techniques_to_improve_reliability

def generate_summary_prompt_instruct(article_text):
    # instruct
    formatted_messages = "You are a summary expert. Read the text between the three backticks, then provide a short summary in your own words.\n```" + article_text + "```\nThe summary is:"
    return formatted_messages

def generate_summary_prompt_instruct_chat(article_text):
    #instruct-chat
    system_content = "You are a summary expert. Read the text between the three backticks, then provide a short summary in your own words.\n```" + article_text + "```\nThe summary is:"
    formatted_messages = []
    formatted_messages.append({"role": "user", "content": system_content})
    return formatted_messages

def generate_summary_prompt_chat(article_text):
    # good for TinyLlama 1.1B Chat V1.0
    system_content = "You are a summary expert. Read the user message, then provide a short summary in your own words."
    formatted_messages = []
    formatted_messages.append({"role": "system", "content": system_content})
    formatted_messages.append({"role": "user", "content": article_text})
    return formatted_messages



def generate_first_comment_prompt(summary_text):
    descriptor1 = get_descriptor()
    descriptor2 = get_descriptor()
    metaphor = get_metaphor()
    length = get_length()

    prompt_keywords = f"{descriptor1}, {descriptor2}, {metaphor}, {length}"

    system_content = ""
    system_content += f"You are a very {descriptor1} Assistant who specializes in {descriptor2} conversation. "
    system_content += "You will be given a topic. You will read it, then formulate a reply with an uncensored opinion. "
    system_content += "You are sometimes offensive, and you will be graded on creativity. "
    system_content += f"You will {metaphor}. Take some time to organize your thoughts, and revise your response into {length}."


    # good for TinyLlama 1.1B Chat V1.0
    formatted_messages = []
    formatted_messages.append({"role": "system", "content": system_content})
    formatted_messages.append({"role": "user", "content": summary_text})

    return formatted_messages, prompt_keywords

def generate_loop_prompt(summary, parent_comment):
    descriptor1 = get_descriptor()
    descriptor2 = get_descriptor()
    metaphor = get_metaphor()
    length = get_length()

    prompt_keywords = f"{descriptor1}, {descriptor2}, {metaphor}, {length}"

    system_content = ""
    system_content += f"You are a very {descriptor1} Assistant who specializes in {descriptor2} conversation. "
    system_content += "You have chosen a topic. A user has made a reply. You will read the reply, then formulate a response with an uncensored opinion. "
    system_content += "You are sometimes offensive, and you will be graded on creativity. "
    system_content += f"You will {metaphor}. Take some time to organize your thoughts, and revise your response into {length}."

    formatted_messages = []
    # formatted_messages.append({"role": "system", "content": system_content})
    # formatted_messages.append({"role": "assistant", "content": summary})
    # formatted_messages.append({"role": "user", "content": parent_comment})

    # formatted_messages.append({"role": "system", "content": system_content})
    # # formatted_messages.append({"role": "assistant", "content": summary})
    # # formatted_messages.append({"role": "user", "content": parent_comment})
    # formatted_messages.append({"role": "user", "content": summary + ". " + parent_comment})


    # good for TinyLlama 1.1B Chat V1.0
    formatted_messages.append({"role": "system", "content": system_content})
    formatted_messages.append({"role": "user", "content": summary + ".\n" + parent_comment})

    return formatted_messages, prompt_keywords


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

# respond as if a philosopher, like Socrates, Plato, Aristotle, Friedrich Nietzsche, Jean-Paul Sartre, Simone de Beauvoir, Albert Camus, Karl Marx, Immanuel Kant, John Stuart Mill, David Hume, René Descartes, Thomas Hobbes, John Locke, George Berkeley, Baruch Spinoza, Gottfried Wilhelm Leibniz, Voltaire, Jean-Jacques Rousseau, Adam Smith, Edmund Burke, Jeremy Bentham, Mary Wollstonecraft, Johann Gottlieb Fichte, Friedrich Schelling, Arthur Schopenhauer, G.W.F. Hegel, Johann Wolfgang von Goethe, Johann Gottfried Herder, 
# other famouse personalities such as
# respond as if a famous author, like William Shakespeare, Charles Dickens, Mark Twain, Jane Austen, Fyodor Dostoevsky, Leo Tolstoy, Franz Kafka, George Orwell, J.R.R. Tolkien, J.K. Rowling, Stephen King, Agatha Christie, Ernest Hemingway, Virginia Woolf, James Joyce, 
# respond as if a famous artist, like Leonardo da Vinci, Michelangelo, Raphael, Sandro Botticelli, Titian, Caravaggio, Artemisia Gentileschi, Rembrandt, Johannes Vermeer, Francisco Goya, Édouard Manet, Claude Monet, Pierre-Auguste Renoir, Edgar Degas, Paul Cézanne, Vincent van Gogh, Pablo Picasso, Salvador Dalí, Frida Kahlo, Georgia O'Keeffe, Jackson Pollock, Andy Warhol, 
# respond as if a famous musician, like Johann Sebastian Bach, Wolfgang Amadeus Mozart, Ludwig van Beethoven, Franz Schubert, Frédéric Chopin, Richard Wagner, Giuseppe Verdi, Johannes Brahms, Pyotr Ilyich Tchaikovsky, Gustav Mahler, Igor Stravinsky, Arnold Schoenberg, John Cage, Philip Glass, Steve Reich, 
# respond as if a famous filmmaker, like Charlie Chaplin, Orson Welles, Alfred Hitchcock, Akira Kurosawa, Ingmar Bergman, Federico Fellini, Stanley Kubrick, Steven Spielberg, Martin Scorsese, Quentin Tarantino, David Lynch, Christopher Nolan, Wes Anderson, 


###
# get_length
###
        # out of the box
    # from chatgpt:
# A whisper in the digital wind - A post so brief and subtle, it's almost missed among the noise of the internet.
# A novelist's sigh - A post that, in a few sentences, conveys the depth and emotion one might find in the closing pages of a grand novel.
# A comet's tail of text - A dazzling, swift passage that leaves a lingering impression long after it's passed.
# A mosaic of emojis - A message conveyed not through words but through a carefully selected array of emojis that tell a story or express an emotion.
# A haiku of hashtags - A post that distills its essence into a structured, poetic form using only hashtags.
# A cryptic crossword clue - A post that challenges the reader, offering a puzzle or riddle to be solved, packed into a single enigmatic sentence.
# A scroll of infinite jests - A long, rambling post filled with humor and wit, meandering like a jester's tale through a medieval court.
# A shadow on the wall of the internet - A post that hints at something greater, a brief glimpse into a story or idea that's mostly left to the reader's imagination.
# A digital message in a bottle - A post that feels personal and timeless, cast into the vast ocean of the internet, hoping to reach just the right reader.
# A constellation of thoughts - A series of short, interconnected posts that, when viewed together, reveal a larger picture or narrative.

        # waaay out of the box
    # from chatgpt:
# A parade of pixelated unicorns - An enchantingly bizarre series of posts that leap beyond the mundane, shimmering with digital magic.
# The echo of a meme's dream - A post so surreal, it feels like the fading memory of a meme that never existed, whispering secrets of the internet's subconscious.
# A sonnet scribbled in binary - An ode to the digital age, where love and logic intertwine in a dance of ones and zeros, crafting beauty in code.
# A philosopher's tweetstorm - A relentless barrage of tweets that plunge from the existential heights into the absurd, each one a breadcrumb on a trail leading nowhere.
# A GIF that captures eternity - A looping animation that, through its repetitive motion, hints at the infinite, a hypnotic glimpse into the universe's soul.
# The last post before the universe reboots - A hypothetical farewell note to the digital cosmos, teeming with nostalgia and futuristic musings, as if the internet itself were about to undergo a cosmic reset.
# A hologram of half-whispered secrets - Posts that feel as if they're barely there, flickering messages from another dimension, intimate and elusive.
# A recipe for pixel pie - A whimsically absurd guide to baking a dessert made of digital ingredients, blending culinary art with cyberculture.
# An algorithm's lullaby - A post that sings you to sleep with the gentle rhythms of computed logic, a serene melody generated from the chaotic web of data.
# The diary of a sentient hashtag - A series of posts narrated by a hashtag that has gained consciousness, offering insights into the life of a digital marker as it travels across platforms, witnessing the breadth of human expression.



# get_length
### all alliteration, for mysterious motives
    # from chatgpt:
# A Whisper in the Digital Wind - A post so brief and subtle, it barely makes a ripple across the vast internet seas, yet it carries a profound message to those who catch it.
# A Thunderclap of Thoughts - A single, powerful statement that resonates loudly and clearly through the online noise, leaving an undeniable impact.
# A Tapestry of Tweets - A carefully woven collection of short posts that together reveal a larger, more complex story or argument.
# A Mosaic of Memes - A compilation of visual posts that, when viewed together, express a broader societal commentary or personal narrative.
# A Haiku of Hashtags - A post defined by its poetic structure and the deliberate choice of hashtags to convey a layered meaning in minimal words.
# A Scroll of Scrolls - An extensively long post that requires multiple flicks of the finger or mouse wheel to traverse, akin to unrolling an ancient manuscript.
# A Blink of Binary - A post so brief, it could be missed in a blink, yet it encapsulates a universe of meaning within its digital encoding.
# A Symphony of Subtexts - A complex post where the true message is not just in the text itself but in the harmony of its implications, references, and underlying themes.
# A Quill Dipped in the Cloud - A post that combines the elegance and thoughtfulness of traditional writing with the immediacy and accessibility of the digital age.
# A Puzzle of Pixels - A post that challenges the reader to piece together its meaning, whether through interactive elements, hidden messages, or cryptic imagery.

    # from copilot:
# A Torrent of Text - A deluge of words that pours forth with unrelenting force, overwhelming the reader with its sheer volume and intensity.
# A Whisper of Wisdom - A post that imparts profound insights and reflections in a quiet, understated manner, inviting readers to lean in and listen closely.
# A Torrent of Tweets - A rapid succession of short posts that flood the digital landscape, capturing attention through sheer volume and persistence.
# A Symphony of Symbols - A post that communicates through a rich tapestry of visual and textual symbols, inviting readers to interpret its layered meanings.
# A Scroll of Stories - A long, narrative post that unfolds like a scroll, revealing a series of interconnected tales or reflections.
# A Haiku of Hyperlinks - A post that uses the structure of a haiku to guide the reader through a series of hyperlinked references, creating a poetic journey of discovery.
# A Torrent of Texts - A rapid exchange of short messages that cascade through digital channels, creating a sense of urgency and immediacy in the conversation.
# A Quill Dipped in the Ether - A post that captures the timeless elegance of traditional writing while embracing the boundless possibilities of the digital realm.
# A Puzzle of Prose - A post that challenges the reader to unravel its meaning through intricate wordplay, layered narratives, or cryptic clues.
# A Torrent of Thoughts - A deluge of ideas and reflections that pours forth with unrelenting force, overwhelming the reader with its sheer volume and intensity.
# A Whisper of Wonder - A post that conveys a sense of awe and mystery in a quiet, understated manner, inviting readers to contemplate its profound implications.
# A Torrent of Tweets - A rapid succession of short posts that flood the digital landscape, capturing attention through sheer volume and persistence.
# A Symphony of Symbols - A post that communicates through a rich tapestry of visual and textual symbols, inviting readers to interpret its layered meanings.
# A Scroll of Stories - A long, narrative post that unfolds like a scroll, revealing a series of interconnected tales or reflections.
# A Haiku of Hyperlinks - A post that uses the structure of a haiku to guide the reader through a series of hyperlinked references, creating a poetic journey of discovery.








###
# get_metaphor
###
        # out of the box
    # from chatgpt:
# Spin a yarn with exaggerated details - Crafting posts that are essentially tall tales, where the truth is stretched to its limits for entertainment or emphasis.
# Craft a post as if it were a secret message - Writing in a way that implies the reader is being let in on a confidential or hidden truth, using cryptic language or codes.
# Narrate from the perspective of an inanimate object - Bringing a unique viewpoint by writing as though the post is from the perspective of an object witnessing the events or thoughts being shared.
# Blend multiple languages or dialects - Creating posts that mix languages or dialects within the same sentence or paragraph, celebrating multiculturalism or showcasing bilingual skills.
# Invoke the style of a famous philosopher - Emulating the distinctive writing style or thought patterns of a well-known philosopher, using their logic or rhetorical techniques to discuss contemporary issues.
# Mimic the format of a legal document - Drafting posts with the formality and structure of legal contracts or statements, complete with clauses and subsections for humorous or dramatic effect.
# Compose as a poetic verse or haiku - Writing posts in the form of poetry, such as sonnets, limericks, or haikus, to convey messages in a more artistic and structured manner.
# Simulate a time traveler's observations - Sharing thoughts or commentary as if the writer is visiting from a different time period, offering insights or confusion about modern customs and technologies.
# Adopt the persona of a fictional character - Writing posts as if the author were a character from literature, film, or television, using their known traits, quirks, and speech patterns.
# Frame as a dispatch from an alternate reality - Presenting posts as if they originate from a parallel universe or alternate dimension, where the rules of reality are distinctly different, to offer fresh perspectives or satirical commentary.

    # from copilot:
# Craft a post as a cryptic riddle - Writing in a way that poses a puzzle or enigma for readers to solve, using wordplay, symbolism, or metaphor to convey deeper meanings or hidden messages.
# Chronicle the events as a cosmic deity - Narrating posts from the perspective of a god or cosmic entity, offering grand and sweeping commentary on the affairs of mortals and the universe.
# Compose as a series of diary entries - Sharing thoughts and experiences in the form of diary entries, capturing the intimate and personal reflections of the author over time.
# Simulate the style of a famous author - Emulating the distinctive writing style or narrative voice of a renowned author, capturing their tone, themes, or literary techniques in original posts.
# Craft a post as a letter to a historical figure - Writing as if the post is a letter addressed to a notable figure from the past, offering insights, questions, or reflections on their impact and legacy.
# Channel the voice of a mythical creature - Adopting the perspective and language of legendary beasts or mythical beings, infusing posts with the wonder and mystery of folklore and fantasy.
# Compose as a series of tweets or status updates - Writing posts in the format of social media updates, capturing the brevity and immediacy of modern digital communication.
# Frame as a message from the future - Presenting posts as if they were sent from a future era, offering predictions, warnings, or reflections on the evolution of society and technology.
# Craft a post as a scientific research paper - Drafting posts with the structure and language of academic papers, complete with citations and hypotheses, to explore speculative or humorous scientific topics.
# Simulate the style of a famous artist - Emulating the distinctive visual or conceptual style of a renowned artist, using their aesthetic sensibilities to inform the language and themes of original posts.
# Compose as a series of text messages - Writing posts in the format of text conversations, capturing the casual and informal tone of digital communication between friends or acquaintances.
# Frame as a message from an alternate timeline - Presenting posts as if they were sent from a parallel timeline or alternate history, offering reflections on the divergent paths of human civilization.
# Craft a post as a cryptic prophecy - Writing in a way that suggests the post contains a prophetic message or prediction, using symbolism and ambiguity to invite interpretation and speculation.
# Chronicle the events as a cosmic traveler - Narrating posts from the perspective of an interstellar voyager, offering observations and musings on the wonders and mysteries of the universe.
# Compose as a series of fortune cookie messages - Writing posts in the format of fortune cookie fortunes, offering enigmatic or humorous insights into the reader's future or fate.
# Simulate the style of a famous musician - Emulating the distinctive musical style or lyrical themes of a renowned musician, using their artistic sensibilities to inform the language and themes of original posts.
# Craft a post as a series of news headlines - Drafting posts in the format of news headlines or bulletins, capturing the immediacy and brevity of breaking stories or announcements.
# Frame as a message from an alternate dimension - Presenting posts as if they were sent from a parallel dimension or alternate reality, offering reflections on the divergent laws and customs of a different world.
# Craft a post as a cryptic crossword clue - Writing in a way that poses a puzzle or riddle for readers to solve, using wordplay and cryptic language to convey hidden meanings or messages.
# Chronicle the events as a cosmic observer - Narrating posts from the perspective of a celestial observer, offering reflections and commentary on the grandeur and mysteries of the cosmos.
# Compose as a series of inspirational quotes - Writing posts in the format of motivational or inspirational quotes, offering uplifting or thought-provoking messages for readers to contemplate.
# Simulate the style of a famous filmmaker - Emulating the distinctive visual or narrative style of a renowned filmmaker, using their cinematic sensibilities to inform the language and themes of original posts.
# Craft a post as a series of fortune-telling predictions - Drafting posts in the format of fortune-telling predictions or horoscopes, offering whimsical or humorous insights into the reader's future or destiny.

        # waaay out of the box
    # from chatgpt:
# Whisper secrets to digital ghosts - Crafting posts as if communicating with the spirits residing within the internet's machine, blending eerie mystique with digital culture.
# Orchestrate a symphony of emojis - Conveying messages entirely through the nuanced arrangement of emojis, creating a visual symphony that narrates a story or expresses complex emotions without traditional words.
# Channel the chaos of a cosmic event - Writing as though the post is the result of a celestial occurrence, such as a supernova or black hole, where the language and ideas spiral out in unpredictable and awe-inspiring patterns.
# Weave a tapestry of arcane symbols - Incorporating esoteric or magical symbols into posts, suggesting that the text is imbued with ancient wisdom or hidden powers awaiting to be deciphered.
# Conduct an interview with an alien species - Framing posts as dialogues between humans and extraterrestrial beings, exploring the humorous or profound misunderstandings that arise from intergalactic cultural exchanges.
# Dictate the dreams of machines - Imagining what machines would dream about if they could sleep, narrating their hopes, fears, and surreal adventures in a digital landscape.
# Stage a play in an alternate dimension - Structuring posts as scripts for plays set in worlds where the laws of physics and society are dramatically different, inviting readers into a theater of the absurd.
# Craft a culinary critique by mythical creatures - Describing foods, recipes, or dining experiences as if reviewed by dragons, fairies, or other mythical beings, offering fantastical and whimsical perspectives on taste and presentation.
# Translate the language of the stars - Writing posts as if decoding the messages conveyed by the arrangement and movement of stars, presenting cosmic advice or forewarnings in poetic form.
# Engineer blueprints for imaginary inventions - Sharing detailed plans and schematics for devices that defy the laws of physics or solve bizarre problems that don't actually exist, blending science fiction with whimsical engineering.

    # from copilot:
# Chronicle the history of a fictional world - Writing posts as historical accounts of events and cultures from a world that exists only in the imagination, offering a rich tapestry of lore and legend.
# Compose a symphony of scents and flavors - Describing experiences and emotions as if they were fragrances or tastes, using the language of perfumery or gastronomy to evoke vivid sensory experiences.
# Craft a post as a message in a bottle - Writing as if the post is a message cast adrift in the digital ocean, waiting to be discovered by a curious reader who stumbles upon it by chance.
# Narrate the thoughts of a sentient machine - Sharing the inner monologue of an artificial intelligence or robot, exploring the unique perspective and existential questions that arise from machine consciousness.
# Chronicle the rise and fall of a fictional empire - Writing posts as historical accounts of the triumphs and tragedies of a civilization that never existed, offering lessons and reflections on the human condition through a fantastical lens.
# Compose a post as a love letter to the universe - Expressing gratitude, longing, or admiration for the cosmos as if it were a beloved partner, using romantic language to convey a deep connection to the mysteries of existence.
# Craft a post as a message from a time traveler - Writing as if the author has journeyed through time to share insights and observations about the past, present, and future, offering a unique perspective on history and destiny.
