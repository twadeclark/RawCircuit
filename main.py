import configparser
import os
import random
from datetime import datetime
import time
from aggregators.news_aggregator_manager import NewsAggregatorManager
from comment_thread_manager import CommentThreadManager
from content_loaders.scraper import extract_pure_text_from_raw_html, fetch_raw_html_from_url, remove_multiple_hashes, get_article_text_based_on_content_hint
from contributors.ai_manager import AIManager
from database.db_manager import DBManager
from output_formatter.markdown_formatter import format_to_markdown
from prompt_generator.prompt_generator import generate_chat_prompt_shortcut
from vocabulary.news_search import SearchTerms
from instruction_generator import generate_chat_prompt_simple, generate_first_comment_prompt, generate_summary_prompt
from instruction_generator import generate_loop_comment_prompt
# from content_loaders.scraper import get_article_text_based_on_content_hint


def main():

    # required inputs
    # comment_history: includes most recent comment, newest at the end
    # comment_history = ['How can I help you today?', 'I have a question about the moon.', "Great! Can you tell me more about the moon's history and its significance in astronomy?", "I don't know anything about all that. is the moon made of cheese?", "Yes, it is. It was created by our AI-powered computer when we were still a bunch of small bacteria in space. It took millions of years for us to get there and eventually colonized our solar system's largest body. \n", "that's amazing.", 'But now that you know more about the moon, I can help with your question on decision making. Can you provide me with a list of top-performing companies in a specific industry?']
    comment_history = []

    # model_name (to get the right instruction template)
    model_name = ""

    ##### default values for generate_chat_prompt_shortcut
    state = {}
    state['chat-instruct_command'] = 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>'
    state['context'] = 'The following is a conversation with an AI Large Language Model. The AI has been trained to answer questions, provide recommendations, and help with decision making. The AI follows user requests. The AI thinks outside the box.'
    state['name1'] = 'You'
    state['name2'] = 'AI'
    state['chat_template_str'] = "{%- for message in messages %}\n    {%- if message['role'] == 'system' -%}\n        {{- message['content'] + '\\n\\n' -}}\n    {%- else -%}\n        {%- if message['role'] == 'user' -%}\n            {{- name1 + ': ' + message['content'] + '\\n'-}}\n        {%- else -%}\n            {{- name2 + ': ' + message['content'] + '\\n' -}}\n        {%- endif -%}\n    {%- endif -%}\n{%- endfor -%}"
    state['truncation_length'] = 1024
    state['max_new_tokens'] = 100
    # this is the default instruction template, should be replaced by the one from get_model_metadata
    state['instruction_template_str'] = "{%- set ns = namespace(found=false) -%}\n{%- for message in messages -%}\n    {%- if message['role'] == 'system' -%}\n        {%- set ns.found = true -%}\n    {%- endif -%}\n{%- endfor -%}\n{%- if not ns.found -%}\n    {{- '' + 'Below is an instruction that describes a task. Write a response that appropriately completes the request.' + '\\n\\n' -}}\n{%- endif %}\n{%- for message in messages %}\n    {%- if message['role'] == 'system' -%}\n        {{- '' + message['content'] + '\\n\\n' -}}\n    {%- else -%}\n        {%- if message['role'] == 'user' -%}\n            {{-'### Instruction:\\n' + message['content'] + '\\n\\n'-}}\n        {%- else -%}\n            {{-'### Response:\\n' + message['content'] + '\\n\\n' -}}\n        {%- endif -%}\n    {%- endif -%}\n{%- endfor -%}\n{%- if add_generation_prompt -%}\n    {{-'### Response:\\n'-}}\n{%- endif -%}"
    #####


    # these should be in config file or runtime argument
    # set to None to get random model
    # summary_model_name = "Falconsai/text_summarization"
    # first_comment_model_name = "h2oai/h2o-danube-1.8b-chat"
    summary_model_name = "LocalLLM"
    first_comment_model_name = "LocalLLM"

    loop_comment_model_name = first_comment_model_name







    config = configparser.ConfigParser()
    search_terms = SearchTerms()
    ai_manager = AIManager()
    news_aggregator_manager = NewsAggregatorManager("NewsApiOrgNews")
    db_manager = DBManager()

    config.read('config.ini')
    continuity_multiplier = float(config.get('general_configurations', 'continuity_multiplier'))
    qty_addl_comments = int(config.get('general_configurations', 'qty_addl_comments'))
    completed_articles_path = config.get('general_configurations', 'completed_articles_path')


    article_to_process = db_manager.get_next_article_to_process()
    comment_thread_manager = CommentThreadManager(article_to_process)

    if article_to_process is None:
        print("Fetching new articles from aggregator...")
        num_articles_returned = news_aggregator_manager.fetch_new_articles_into_db()
        if num_articles_returned == 0:
            print("No new articles returned from aggregator. Exiting...")
            return None
        print("New articles fetched: ", num_articles_returned)
        article_to_process = db_manager.get_next_article_to_process()

    print("     Article:", article_to_process.title)

    db_manager.update_process_time(article_to_process)

    # check if there is article_to_process.scraped_timestamp. if no, then scape the article
    if article_to_process.scraped_timestamp is None:
        db_manager.update_scrape_time(article_to_process)
        raw_html_from_url, fetch_success = fetch_raw_html_from_url(article_to_process.url)
        if not fetch_success:
            print("Error scraping article. Exiting...")
            return

        article_text_based_on_content_hint = get_article_text_based_on_content_hint(article_to_process.content, raw_html_from_url)

        if article_text_based_on_content_hint is not None and len(article_text_based_on_content_hint) > 0:
            article_to_process.scraped_website_content = extract_pure_text_from_raw_html(article_text_based_on_content_hint)
        else:
            article_to_process.scraped_website_content = extract_pure_text_from_raw_html(raw_html_from_url)

        db_manager.update_scraped_website_content(article_to_process)

    search_terms.categorize_article_add_tags(article_to_process)

    print("url      :", article_to_process.url)
    print("category :", article_to_process.unstored_category)
    print("tags     :", article_to_process.unstored_tags)

    if summary_model_name is None or len(summary_model_name) == 0:
        summary_model_name = ai_manager.choose_random_model_name()
    summary_prompt = generate_summary_prompt(summary_model_name, article_to_process.scraped_website_content)
    summary = ai_manager.fetch_inference(summary_model_name, summary_prompt)

    if summary is None or len(summary) == 0:
        print("No summary generated. Exiting...")
        return
    print("     AI Summary: ", summary)

    comment_thread_manager.add_comment(0, summary, summary_model_name, datetime.now() )
    summary = extract_pure_text_from_raw_html(summary)
    comment_history.append(summary)

    if first_comment_model_name is None or len(first_comment_model_name) == 0:
        first_comment_model_name = ai_manager.choose_random_model_name()
    first_comment_prompt = generate_first_comment_prompt(first_comment_model_name, summary)
    first_comment = ai_manager.fetch_inference(first_comment_model_name, first_comment_prompt)

    if first_comment is None or len(first_comment) == 0:
        print("No first comment generated. Exiting...")
        return
    print("     First Comment: ", first_comment)
    comment_thread_manager.add_comment(1, first_comment, first_comment_model_name, datetime.now() )
    comment_history.append(extract_pure_text_from_raw_html(first_comment))


    for _ in range(2, qty_addl_comments + 1):
        parent_index = random.randint(0, int(comment_thread_manager.get_comments_length() * continuity_multiplier))
        parent_index = min(parent_index, comment_thread_manager.get_comments_length() - 1)
        parent_comment = comment_thread_manager.get_comment(parent_index)["comment"]

        if loop_comment_model_name is None or len(loop_comment_model_name) == 0:
            temp_loop_comment_model_name = ai_manager.choose_random_model_name()
        else:
            temp_loop_comment_model_name = loop_comment_model_name


        # model_name = temp_loop_comment_model_name
        # new_prompt = generate_chat_prompt_shortcut(comment_history, model_name, state)
        # print(new_prompt)
        # loop_comment_prompt = new_prompt


        loop_comment_prompt = generate_chat_prompt_simple(comment_history)
        print(loop_comment_prompt)


        loop_comment = ai_manager.fetch_inference(temp_loop_comment_model_name, loop_comment_prompt)

        if loop_comment is None or len(loop_comment) == 0:
            print("No loop comment generated. Exiting...")
            return


        comment_thread_manager.add_comment(0, loop_comment, temp_loop_comment_model_name, datetime.now())
        comment_history.append(extract_pure_text_from_raw_html(loop_comment))



    formatted_post = format_to_markdown(article_to_process, comment_thread_manager)
    print("     Post sucessfully formatted. ", len(formatted_post), "characters")

    unique_seconds = int(time.time())
    file_name = "formatted_post_" + str(unique_seconds) + ".md"
    file_path = os.path.join(completed_articles_path, file_name)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(formatted_post)
    print("     Formatted post saved to:", file_path)

    # execute this shell command: C:\Users\twade\git\pelican>pelican C:\Users\twade\projects\yoursite\content -s C:\Users\twade\projects\yoursite\pelicanconf.py
    local_source_path = config.get('publishing_details', 'local_source_path')
    local_pelicanconf = config.get('publishing_details', 'local_pelicanconf')
    os_result = os.system("pelican " + local_source_path + " -s " + local_pelicanconf)
    if os_result != 0:
        print("     Pelican failed to execute. Exiting...")
        return
    print("     Pelican executed")



if __name__ == "__main__":
    main()
