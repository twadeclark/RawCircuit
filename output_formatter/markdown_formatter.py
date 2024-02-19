import re
from dateutil import parser

# 🦾  ♻️   🚡  🪒  🪩  🪤  🧉  🐚  🪶  🃏  🧃  🪽  🫎  🪬  🧌  🏺  🧦  🥌  📇  🗃️  🦪

def format_to_markdown(article, comment_thread_manager):
    markdown = ""

    title = re.sub(r"\[.*\]", "", article.title).strip()
    title = re.sub(r'\([^)]*\)', '', article.title)
    title = re.sub(r'\{[^)]*\}', '', article.title)

    comment = comment_thread_manager.get_comment(0)

    markdown += (f"Title: {title}\n")
    markdown += (f"Date: {parse_date_into_pretty_string(comment_thread_manager.get_start_time())}\n")
    markdown += (f"Authors: {comment["author"]}\n")
    markdown += (f"Tags: {comment_thread_manager.get_tags_comma_separated()}\n")
    markdown += (f"Category: {comment_thread_manager.get_category()}\n")
    markdown += (f"featured_image: {article.url_to_image}\n")
    markdown += (f"comments_intro: {comment["comment"]}\n")

    markdown += ("<span style='font-size: smaller;'>")
    markdown += (f"[original article]({article.url}) from *{article.source_name}* by *{article.author}* at *{parse_date_into_pretty_string(article.published_at)}* ")
    markdown += ("</span>\n\n")
    markdown += ("***\n\n")

    for i in range(1, comment_thread_manager.get_comments_length()):
        comment = comment_thread_manager.get_comment(i)
        markdown += (f"<span style='font-size: smaller;'>**{comment["author"]}** *on {parse_date_into_pretty_string(comment["date"])}*</span>\n\n")

        p = int(comment["parent"])
        if (p + 1) != i :
            parent_commenter = comment_thread_manager.get_comment(p)["author"]
            markdown += (f">*{parent_commenter} wrote:*\n\n")
            parent_comment = comment_thread_manager.get_comment(p)["comment"]
            parent_comment = re.sub(r"[\n\r]", " ", parent_comment)
            markdown += (f"><span style='font-size: smaller;'>{parent_comment}</span>\n\n")

        markdown += (f"{comment["comment"]}\n\n")

        markdown += get_badges(comment["prompt_keywords"])

        markdown += ("\n\n***\n\n")

    if article.summary_dump:
        markdown += (f"🦪 <span style='font-size: xx-small;'>View Source for Original Content.</span> <!-- {str(article.shortened_content).replace("\n", " ")} -->\n")
        markdown += (f"⚗️ <span style='font-size: xx-small;'>View Source for Summaries.</span> <!-- {article.summary_dump.replace("\n", " ")} -->\n")

    markdown += (f"⏱️ <span style='font-size: xx-small;'>Processed in {comment_thread_manager.get_duration()}</span>\n") #  ⏱️  ⌛

    return markdown

def get_badges(prompt_keywords):
    ret_val = ""

    prompt_phrase = re.search(r'^(.*?)\|', prompt_keywords).group(1).strip()
    if prompt_phrase is not None and len(prompt_phrase) > 0:
        arrow_chars = '↜↝↫↬↭↯↰↱↲↳↴↵↶↷↸↹↺↻⇜⇝'
        char_pos = sum(ord(c) for c in prompt_phrase) % (len(arrow_chars))
        selected_arrow = arrow_chars[char_pos]
        ret_val += (f"<span title='{prompt_phrase}'> 🎭{selected_arrow}</span> ∙ ")

    if 'max_tokens' in prompt_keywords:
        max_tokens = int(re.search(r'max_tokens: (\d+)', prompt_keywords).group(1)) # 25 - 250
        max_tokens_rotate = int(60 - ((max_tokens - 25) / 3)) # 25 - 500
        ret_val += (f"<span title='max_tokens = {max_tokens}'> 🪙</span><span style='display: inline-block; transform: rotate({max_tokens_rotate}deg);'>→</span> ∙ ")

    if 'max_new_tokens' in prompt_keywords:
        max_new_tokens = int(re.search(r'max_new_tokens: (\d+)', prompt_keywords).group(1)) # 25 - 250
        max_new_tokens_rotate = int(60 - ((max_new_tokens - 25) / 3)) # 25 - 500
        ret_val += (f"<span title='max_new_tokens = {max_new_tokens}'> 🪙</span><span style='display: inline-block; transform: rotate({max_new_tokens_rotate}deg);'>→</span> ∙ ")

    if 'max_length' in prompt_keywords:
        max_length = int(re.search(r'max_length: (\d+)', prompt_keywords).group(1)) # 25 - 250
        max_length_rotate = int(60 - ((max_length - 25) / 3)) # 25 - 500
        ret_val += (f"<span title='max_length = {max_length}'> 🪙</span><span style='display: inline-block; transform: rotate({max_length_rotate}deg);'>→</span> ∙ ")

    if 'temperature' in prompt_keywords:
        temperature = float(re.search(r'temperature: ([\d.]+)', prompt_keywords).group(1)) # 0 - 2
        temperature_rotate = int((temperature - 1) * -60) # 0 - 2
        temperature_as_string = "{:.1f}".format(temperature)
        ret_val += (f"<span title='temperature = {temperature_as_string}'> 🌡️</span><span style='display: inline-block; transform: rotate({temperature_rotate}deg);'>→</span> ∙ ")

    if 'frequency_penalty' in prompt_keywords:
        frequency_penalty = float(re.search(r'frequency_penalty: ([\d.-]+)', prompt_keywords).group(1)) # -2 - 2
        frequency_penalty_rotate = int(frequency_penalty * -30) # -2 - 2
        frequency_penalty_as_string = "{:.1f}".format(frequency_penalty)
        ret_val += (f"<span title='frequency_penalty = {frequency_penalty_as_string}'> 🪸</span><span style='display: inline-block; transform: rotate({frequency_penalty_rotate}deg);'>→</span> ∙ ")

    if 'presence_penalty' in prompt_keywords:
        presence_penalty = float(re.search(r'presence_penalty: ([\d.-]+)', prompt_keywords).group(1)) # -2 - 2
        presence_penalty_rotate = int(presence_penalty * -30) # -2 - 2
        presence_penalty_as_string = "{:.1f}".format(presence_penalty)
        ret_val += (f"<span title='presence_penalty = {presence_penalty_as_string}'> 🔭</span><span style='display: inline-block; transform: rotate({presence_penalty_rotate}deg);'>→</span>")

    if 'repetition_penalty' in prompt_keywords:
        repetition_penalty = float(re.search(r'repetition_penalty: ([\d.-]+)', prompt_keywords).group(1)) # -2 - 2
        repetition_penalty_rotate = int(repetition_penalty * -30) # -2 - 2
        repetition_penalty_as_string = "{:.1f}".format(repetition_penalty)
        ret_val += (f"<span title='repetition_penalty = {repetition_penalty_as_string}'> 🦤</span><span style='display: inline-block; transform: rotate({repetition_penalty_rotate}deg);'>→</span>")

    return ret_val

def parse_date_into_pretty_string(date):
    try:
        date_time_obj = parser.parse(str(date))
        return date_time_obj.strftime("%d %B %Y at %I:%M %p")
    except ValueError:
        return str(date)
