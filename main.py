import configparser
import os
import random
from datetime import datetime
import time
from aggregators.news_aggregator_manager import NewsAggregatorManager
from content_loaders.scraper import extract_pure_text_from_raw_html, fetch_raw_html_from_url, get_article_text_based_on_content_hint, get_polite_name
from contributors.ai_manager import AIManager
from contributors.huggingface_model_search import HuggingfaceModelSearch
from database.db_manager import DBManager
from output_formatter.comment_thread_manager import CommentThreadManager
from output_formatter.markdown_formatter import format_to_markdown
from output_formatter.publish_pelican import publish_pelican
from output_formatter.upload_directory_to_s3 import upload_directory_to_s3
from prompt_generator.instruction_generator import generate_loop_prompt, generate_first_comment_prompt, generate_summary_prompt
from vocabulary.news_search import SearchTerms

MAX_TOKENS_FOR_SUMMARY = 1500

def main():
    summary_model = None

    summary_model = {
                        "name":"tiiuae/falcon-7b-instruct",
                        "interface":"HuggingFaceInterface",
                        "max_tokens":MAX_TOKENS_FOR_SUMMARY
                    }


    comment_thread_manager = CommentThreadManager()
    config = configparser.ConfigParser()
    config.read('config.ini')
    ai_manager = AIManager(config)
    search_terms = SearchTerms()
    db_manager = DBManager(config['postgresql'])
    news_aggregator_manager = NewsAggregatorManager(config, db_manager, None)

    continuity_multiplier = float(config.get('general_configurations', 'continuity_multiplier'))
    qty_addl_comments = int(config.get('general_configurations', 'qty_addl_comments'))
    number_of_models_to_try = int(config.get('general_configurations', 'number_of_models_to_try'))

    article_to_process = db_manager.get_next_article_to_process()

    if article_to_process is None:
        print("Fetching new articles from aggregator...")
        num_articles_returned = news_aggregator_manager.fetch_new_articles_into_db()
        if num_articles_returned == 0:
            HALTING_ERROR = "HALTING_ERROR: No new articles returned from aggregator. Exiting..."
            print(HALTING_ERROR)
            return HALTING_ERROR
        print("New articles fetched: ", num_articles_returned)
        article_to_process = db_manager.get_next_article_to_process()

    if article_to_process is None:
        HALTING_ERROR = "HALTING_ERROR: article_to_process is None. Exiting..."
        print(HALTING_ERROR)
        return HALTING_ERROR

    db_manager.update_process_time(article_to_process)
    comment_thread_manager.set_article(article_to_process)
    print("Article: ", article_to_process.title)
    print("url    :", article_to_process.url)

    if article_to_process.scraped_website_content is None or len(article_to_process.scraped_website_content) == 0:
        print("Content not found. Scraping article...")

        db_manager.update_scrape_time(article_to_process)
        raw_html_from_url, fetch_success = fetch_raw_html_from_url(article_to_process.url)
        if not fetch_success:
            HALTING_ERROR = "HALTING_ERROR: Error scraping article. Exiting..."
            print(HALTING_ERROR)
            return HALTING_ERROR

        article_to_process.scraped_website_content = extract_pure_text_from_raw_html(raw_html_from_url)
        article_text_based_on_content_hint = get_article_text_based_on_content_hint(article_to_process.content, raw_html_from_url)
        if article_text_based_on_content_hint is not None and len(article_text_based_on_content_hint) > 0:
            article_to_process.scraped_website_content = extract_pure_text_from_raw_html(article_text_based_on_content_hint)

    if article_to_process.scraped_website_content is None or len(article_to_process.scraped_website_content) == 0:
        HALTING_ERROR = "HALTING_ERROR: Error scraping website content. Exiting..."
        print(HALTING_ERROR)
        return HALTING_ERROR

    db_manager.update_scraped_website_content(article_to_process)

    search_terms.categorize_article_add_tags(article_to_process)
    print("category :", article_to_process.unstored_category)
    print("tags     :", article_to_process.unstored_tags)

    summary_prompt, prompt_keywords = generate_summary_prompt(article_to_process.scraped_website_content)
    print("    summary_prompt: ", summary_prompt)

    summary, flavors = None, None
    hfms = HuggingfaceModelSearch(db_manager)

    if summary_model is not None:
        hfms.only_insert_model_into_database_if_not_already_there(summary_model["name"])
        summary, flavors = fetch_summary_and_record_model_results(summary_model, ai_manager, summary_prompt, hfms)
    else:
        while summary is None and number_of_models_to_try > 0:
            number_of_models_to_try = number_of_models_to_try - 1
            summary_model_name = hfms.fetch_next_model_name_from_huggingface()

            if summary_model_name is None:
                HALTING_ERROR = "HALTING_ERROR: No new models available from Huggingface. Exiting... \t" + \
                print(HALTING_ERROR)
                return HALTING_ERROR

            print("    Trying model: ", summary_model_name)
            summary_model = {"name": summary_model_name, "interface":"HuggingFaceInterface", "max_tokens":MAX_TOKENS_FOR_SUMMARY}
            summary, flavors = fetch_summary_and_record_model_results(summary_model, ai_manager, summary_prompt, hfms)

    #TODO: we need to decide what to do if we do not get a summary.
        # we halt currently. maybe we should try another model? or try the next article?
        # same questions for first_comment below
    if summary is None or len(summary) == 0:
        model_name = summary_model["name"] if summary_model["name"] is not None else ""
        article_id = article_to_process.id if article_to_process.id is not None else ""
        HALTING_ERROR = "HALTING_ERROR: No summary generated. Exiting... \t" + \
                        f"article_id: {article_id} \t" + \
                        f"model: {model_name} \t" + \
                        f"length_of_scraped_website_content: {len(article_to_process.scraped_website_content)}"
        print(HALTING_ERROR)
        return HALTING_ERROR

    summary = extract_pure_text_from_raw_html(summary)
    comment_thread_manager.add_comment(0,
                                       summary,
                                       get_polite_name(summary_model["name"]),
                                       prompt_keywords + " | " + flavors,
                                       datetime.now()
                                       )

    first_comment_prompt, prompt_keywords = generate_first_comment_prompt(summary)
    print("    first_comment_prompt: ", first_comment_prompt)

    first_comment_model = summary_model.copy()

    first_comment, flavors = ai_manager.fetch_inference(first_comment_model, first_comment_prompt)
    if first_comment is None or len(first_comment) == 0:
        model_name = first_comment_model["name"] if first_comment_model["name"] is not None else ""
        article_id = article_to_process.id if article_to_process.id is not None else ""
        HALTING_ERROR = "HALTING_ERROR: No first comment generated. Exiting... \t" + \
                        f"article_id: {article_id} \t" + \
                        f"model: {model_name} \t" + \
                        f"length_of_first_comment: {len(first_comment)}"
        print(HALTING_ERROR)
        return HALTING_ERROR

    comment_thread_manager.add_comment(0,
                                       first_comment,
                                       get_polite_name(first_comment_model["name"]),
                                       prompt_keywords  + " | " +  flavors,
                                       datetime.now()
                                       )

    loop_comment_model = summary_model.copy()

    for _ in range(1, qty_addl_comments):
        parent_index = random.randint(0, int(comment_thread_manager.get_comments_length() * continuity_multiplier))
        parent_index = min(parent_index, comment_thread_manager.get_comments_length() - 1)
        parent_comment = comment_thread_manager.get_comment(parent_index)["comment"]

        loop_comment_prompt, prompt_keywords = generate_loop_prompt(summary, parent_comment)
        print("    loop_comment_prompt: ", loop_comment_prompt)

        temp_loop_comment_model = loop_comment_model.copy() # in case we want to change the model for each comment, we do something like this: if loop_comment_model == None: temp_loop_comment_model = ai_manager.get_random_model()

        loop_comment, flavors = ai_manager.fetch_inference(temp_loop_comment_model, loop_comment_prompt)
        if loop_comment is None or len(loop_comment) == 0:
            print(f"No loop comment generated. model: {temp_loop_comment_model["name"]} Skipping...")
            continue

        comment_thread_manager.add_comment(parent_index,
                                           loop_comment,
                                           get_polite_name(temp_loop_comment_model["name"]),
                                           prompt_keywords  + " | " +  flavors,
                                           datetime.now()
                                           )


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

    pushed_to_pelican = "NOT published by Pelican. \t"
    if config.getboolean('publishing_details', 'publish_to_pelican'):
        publish_pelican(config["publishing_details"])
        pushed_to_pelican = "PUBLISHED by Pelican. \t"

    published_to_s3 = "NOT pushed to S3. \t"
    if config.getboolean('aws_s3_bucket_details', 'publish_to_s3'):
        number_of_files_pushed = upload_directory_to_s3(config["aws_s3_bucket_details"], config["publishing_details"]["local_publish_path"])
        published_to_s3 = f"PUSHED files to S3: {number_of_files_pushed} \t"

    article_id = article_to_process.id if article_to_process.id is not None else ""
    SUCCESS =   "SUCCESS: \t" + \
                f"article_id: {article_id} \t" + \
                pushed_to_pelican + \
                published_to_s3 + \
                f"Elapsed time: {comment_thread_manager.get_duration()}"
    print(SUCCESS)
    return SUCCESS

def fetch_summary_and_record_model_results(summary_model, ai_manager, summary_prompt, hfms):
    summary, flavors = None, None
    try:
        summary, flavors = ai_manager.fetch_inference(summary_model, summary_prompt)
        length_of_summary = str(len(summary)) if summary is not None else "None."
        hfms.update_model_record(summary_model["name"], True, "length_of_summary: " + length_of_summary)
    except Exception as e:
        print(f"    Model '{summary_model["name"]}' no worky: ", str(e))
        hfms.update_model_record(summary_model["name"], False, str(e))
    return summary, flavors


if __name__ == "__main__":
    main()
