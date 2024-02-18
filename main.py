import configparser
import os
import random
from datetime import datetime
import time
from aggregators.news_aggregator_manager import NewsAggregatorManager
from content_loaders.scraper import fetch_and_set_scraped_website_content, get_polite_name
from contributors.ai_manager import AIManager
from contributors.huggingface_model_search import HuggingfaceModelSearch
from database.db_manager import DBManager
from output_formatter.comment_thread_manager import CommentThreadManager
from output_formatter.markdown_formatter import format_to_markdown
from output_formatter.publish_pelican import publish_pelican
from output_formatter.upload_directory_to_s3 import upload_directory_to_s3
from prompt_generator.instruction_generator import generate_loop_prompt, generate_first_comment_prompt
from vocabulary.news_search import SearchTerms


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    ai_manager = AIManager(config)
    db_manager = DBManager(config['postgresql'])
    news_aggregator_manager = NewsAggregatorManager(config, db_manager, None)
    comment_thread_manager = CommentThreadManager()
    search_terms = SearchTerms()
    hfms = HuggingfaceModelSearch(db_manager)


    max_tokens_for_summary = config.getint('model_info', 'max_tokens_for_summary')
    interface = config.get('model_info', 'interface')
    model_name = config.get('model_info', 'model_name')
    model = {   "name"      : model_name,
                "interface" : interface,
                "max_tokens": max_tokens_for_summary}
    print("model:", model)


    article_to_process = news_aggregator_manager.get_next_article_to_process()

    db_manager.update_process_time(article_to_process)

    comment_thread_manager.set_article(article_to_process)

    if not article_to_process.scraped_website_content:
        fetch_and_set_scraped_website_content(article_to_process, db_manager)

    search_terms.categorize_article_add_tags(article_to_process)

    article_to_process.shortened_content = ' '.join(article_to_process.scraped_website_content.split()[:(max_tokens_for_summary // 2)])
    print("    shortened_content: ", article_to_process.shortened_content, "\n")




    if model["name"]:
        hfms.only_insert_model_into_database_if_not_already_there(model["name"])
        article_to_process.model = model
        article_to_process.summary, article_to_process.summary_dump = ai_manager.get_summary_and_record_model_results(article_to_process, hfms)
    else:
        cnt = int(config.get('general_configurations', 'number_of_models_to_try'))

        while not article_to_process.summary and cnt > 0:
            cnt -= 1

            model_name_temp = hfms.fetch_next_model_name_from_huggingface()
            if not model_name_temp:
                HALTING_ERROR = "HALTING_ERROR: No new models available from Huggingface. Exiting... \t" + \
                print(HALTING_ERROR)
                return HALTING_ERROR

            model = {   "name"      : model_name_temp,
                        "interface" : model["interface"],
                        "max_tokens": max_tokens_for_summary
                                        }
            print("\n    Trying model: ", model["name"])

            article_to_process.summary, article_to_process.summary_dump = ai_manager.get_summary_and_record_model_results(article_to_process, hfms)

        article_to_process.model = model



    if not article_to_process.summary:
        HALTING_ERROR = "HALTING_ERROR: No summary generated. Exiting... \t" + \
                        f"article_id: {article_to_process.id or ""} \t" + \
                        f"model: {article_to_process.model["name"] or ""} \t" + \
                        f"length_of_scraped_website_content: {len(article_to_process.scraped_website_content)}"
        print(HALTING_ERROR)
        return HALTING_ERROR

    comment_thread_manager.add_comment(0,
                                       article_to_process.summary,
                                       get_polite_name(article_to_process.model["name"]),
                                       "summary | summary",
                                       datetime.now()
                                       )



    ### fetch first comment
    article_to_process.first_comment_prompt, article_to_process.first_comment_prompt_keywords = generate_first_comment_prompt(article_to_process.summary)
    print("    first_comment_prompt: ", article_to_process.first_comment_prompt)

    article_to_process.first_comment, article_to_process.first_comment_flavors = ai_manager.fetch_inference(article_to_process.model, article_to_process.first_comment_prompt)

    if not article_to_process.first_comment:
        HALTING_ERROR = "HALTING_ERROR: No first comment generated. Exiting... \t" + \
                        f"article_id: {article_to_process.id or ""} \t" + \
                        f"model: {article_to_process.model["name"] or ""}"
        print(HALTING_ERROR)
        return HALTING_ERROR

    comment_thread_manager.add_comment(0,
                                       article_to_process.first_comment,
                                       get_polite_name(article_to_process.model["name"]),
                                       article_to_process.first_comment_prompt_keywords  + " | " +  article_to_process.first_comment_flavors,
                                       datetime.now()
                                       )



    ### generate additional comments
    qty_addl_comments = int(config.get('general_configurations', 'qty_addl_comments'))
    continuity_multiplier = float(config.get('general_configurations', 'continuity_multiplier'))

    for _ in range(1, qty_addl_comments):
        parent_index = random.randint(0, int(comment_thread_manager.get_comments_length() * continuity_multiplier))
        parent_index = min(parent_index, comment_thread_manager.get_comments_length() - 1)
        parent_comment = comment_thread_manager.get_comment(parent_index)["comment"]

        loop_comment_prompt, prompt_keywords = generate_loop_prompt(article_to_process.summary, parent_comment)
        print("    loop_comment_prompt: ", loop_comment_prompt)

        loop_comment, flavors = ai_manager.fetch_inference(article_to_process.model, loop_comment_prompt)
        if not loop_comment:
            print(f"No loop comment generated. model: {article_to_process.model["name"]} Skipping...")
            continue

        comment_thread_manager.add_comment(parent_index,
                                           loop_comment,
                                           get_polite_name(article_to_process.model["name"]),
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

    article_id = article_to_process.id or ""
    SUCCESS =   "SUCCESS: \t" + \
                f"article_id: {article_id} \t" + \
                pushed_to_pelican + \
                published_to_s3 + \
                f"Elapsed time: {comment_thread_manager.get_duration()}"
    print(SUCCESS)
    return SUCCESS



if __name__ == "__main__":
    main()
