import configparser
import os
import random
from datetime import datetime
import time
from aggregators.news_aggregator_manager import NewsAggregatorManager
from comment_thread_manager import CommentThreadManager
from content_loaders.scraper import extract_pure_text_from_raw_html, fetch_raw_html_from_url, get_article_text_based_on_content_hint
from contributors.ai_manager import AIManager
from database.db_manager import DBManager
from output_formatter.markdown_formatter import format_to_markdown
from vocabulary.news_search import SearchTerms
from instruction_generator import generate_chat_prompt_simple, generate_first_comment_prompt, generate_summary_prompt


def main():

    #TODO: move these to config.ini
    summary_model_name = "LocalLLM"
    first_comment_model_name = "LocalLLM"
    loop_comment_model_name = first_comment_model_name

    ##### default values for generate_chat_prompt_shortcut
    # state = {}
    # state['chat-instruct_command'] = 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>'
    # state['context'] = 'The following is a conversation with an AI Large Language Model. The AI has been trained to answer questions, provide recommendations, and help with decision making. The AI follows user requests. The AI thinks outside the box.'
    # state['name1'] = 'You'
    # state['name2'] = 'AI'
    # state['chat_template_str'] = "{%- for message in messages %}\n    {%- if message['role'] == 'system' -%}\n        {{- message['content'] + '\\n\\n' -}}\n    {%- else -%}\n        {%- if message['role'] == 'user' -%}\n            {{- name1 + ': ' + message['content'] + '\\n'-}}\n        {%- else -%}\n            {{- name2 + ': ' + message['content'] + '\\n' -}}\n        {%- endif -%}\n    {%- endif -%}\n{%- endfor -%}"
    # state['truncation_length'] = 1024
    # state['max_new_tokens'] = 100
    # # this is the default instruction template, should be replaced by the one from get_model_metadata
    # state['instruction_template_str'] = "{%- set ns = namespace(found=false) -%}\n{%- for message in messages -%}\n    {%- if message['role'] == 'system' -%}\n        {%- set ns.found = true -%}\n    {%- endif -%}\n{%- endfor -%}\n{%- if not ns.found -%}\n    {{- '' + 'Below is an instruction that describes a task. Write a response that appropriately completes the request.' + '\\n\\n' -}}\n{%- endif %}\n{%- for message in messages %}\n    {%- if message['role'] == 'system' -%}\n        {{- '' + message['content'] + '\\n\\n' -}}\n    {%- else -%}\n        {%- if message['role'] == 'user' -%}\n            {{-'### Instruction:\\n' + message['content'] + '\\n\\n'-}}\n        {%- else -%}\n            {{-'### Response:\\n' + message['content'] + '\\n\\n' -}}\n        {%- endif -%}\n    {%- endif -%}\n{%- endfor -%}\n{%- if add_generation_prompt -%}\n    {{-'### Response:\\n'-}}\n{%- endif -%}"
    #####

    ai_manager = AIManager()
    comment_history = []
    config = configparser.ConfigParser()
    config.read('config.ini')
    search_terms = SearchTerms()
    news_aggregator_manager = NewsAggregatorManager("NewsApiOrgNews")
    db_manager = DBManager()

    continuity_multiplier = float(config.get('general_configurations', 'continuity_multiplier'))
    qty_addl_comments = int(config.get('general_configurations', 'qty_addl_comments'))

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
    print("url      :", article_to_process.url)

    db_manager.update_process_time(article_to_process)

    if article_to_process.scraped_timestamp is None: # check if there is article_to_process.scraped_timestamp. if no, then scape the article
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

    print("category :", article_to_process.unstored_category)
    print("tags     :", article_to_process.unstored_tags)

    summary_model_polite_name, summary_model = ai_manager.return_model_by_name(summary_model_name)
    summary_prompt = generate_summary_prompt(article_to_process.scraped_website_content)
    print("    summary_prompt: ", summary_prompt, "\n")
    summary = ai_manager.fetch_inference(summary_model, summary_prompt)

    if summary is None or len(summary) == 0:
        print("No summary generated. Exiting...")
        return

    comment_thread_manager.add_comment(0, summary, summary_model_polite_name, datetime.now() )
    summary = extract_pure_text_from_raw_html(summary)
    comment_history.append(summary)

    first_comment_polite_name, first_comment_model = ai_manager.return_model_by_name(first_comment_model_name)
    first_comment_prompt = generate_first_comment_prompt(summary)
    print("    first_comment_prompt: ", first_comment_prompt, "\n")
    first_comment = ai_manager.fetch_inference(first_comment_model, first_comment_prompt)

    if first_comment is None or len(first_comment) == 0:
        print("No first comment generated. Exiting...")
        return

    comment_thread_manager.add_comment(0, first_comment, first_comment_polite_name, datetime.now() )
    comment_history.append(extract_pure_text_from_raw_html(first_comment))

    loop_num = 1

    for _ in range(1, qty_addl_comments):
        parent_index = random.randint(0, int(comment_thread_manager.get_comments_length() * continuity_multiplier))
        parent_index = min(parent_index, comment_thread_manager.get_comments_length() - 1)
        parent_comment = comment_thread_manager.get_comment(parent_index)["comment"]

        temp_loop_polite_name, temp_loop_comment_model = ai_manager.return_model_by_name(loop_comment_model_name)

        # model_name = temp_loop_comment_model_name
        # new_prompt = generate_chat_prompt_shortcut(comment_history, model_name, state)
        # print(new_prompt)
        # loop_comment_prompt = new_prompt

        loop_comment_prompt = generate_chat_prompt_simple(comment_history)
        print("    loop_comment_prompt: ", loop_comment_prompt, "\n")

        loop_comment = ai_manager.fetch_inference(temp_loop_comment_model, loop_comment_prompt)

        if loop_comment is None or len(loop_comment) == 0:
            print("No loop comment generated. Skipping...")
            continue

        comment_thread_manager.add_comment(loop_num, loop_comment, temp_loop_polite_name, datetime.now())
        comment_history.append(extract_pure_text_from_raw_html(loop_comment))
        loop_num += 1


    ### formatting and publishing
    local_content_path = config.get('publishing_details', 'local_content_path')
    formatted_post = format_to_markdown(article_to_process, comment_thread_manager)
    print("     Post sucessfully formatted. ", len(formatted_post), "characters")

    unique_seconds = int(time.time())
    file_name = "formatted_post_" + str(unique_seconds) + ".md"
    file_path = os.path.join(local_content_path, file_name)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(formatted_post)
    print("     Formatted post saved to:", file_path)

    publish_pelican(config)


def publish_pelican(config):
    # execute this shell command: C:\Users\twade\git\pelican>pelican C:\Users\twade\projects\PelicanRawCircuit\content -s C:\Users\twade\projects\PelicanRawCircuit\pelicanconf.py -o C:\Users\twade\projects\PelicanRawCircuit\output -o C:\\Users\\twade\\projects\\PelicanRawCircuit\\output
    local_content_path = config.get('publishing_details', 'local_content_path')
    local_pelicanconf = config.get('publishing_details', 'local_pelicanconf')
    local_publish_path = config.get('publishing_details', 'local_publish_path')
    os_result = os.system("pelican " + local_content_path + " -s " + local_pelicanconf + " -o " + local_publish_path)
    if os_result != 0:
        print("     Pelican failed to execute. Exiting...")
        return
    print("     Pelican executed")


if __name__ == "__main__":
    main()
