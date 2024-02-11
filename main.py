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
from output_formatter.publish_pelican import publish_pelican
from output_formatter.upload_directory_to_s3 import upload_directory_to_s3
from vocabulary.news_search import SearchTerms
from prompt_generator.instruction_generator import generate_loop_prompt, generate_first_comment_prompt, generate_summary_prompt


def main():
    #TODO: move these to config.ini, also add random or round robin for an interface if in a loop
    # or LocalLLM
    summary_model_name = "LocalLLM" # set to None to choose a random model
    first_comment_model_name = summary_model_name # set to None to choose a random model
    loop_comment_model_name = summary_model_name # set to None to choose a random model

    comment_thread_manager = CommentThreadManager()
    config = configparser.ConfigParser()
    config.read('config.ini')
    ai_manager = AIManager(config)
    search_terms = SearchTerms()
    db_manager = DBManager(config['postgresql'])
    news_aggregator_manager = NewsAggregatorManager(config, db_manager, None)

    comment_history = []
    continuity_multiplier = float(config.get('general_configurations', 'continuity_multiplier'))
    qty_addl_comments = int(config.get('general_configurations', 'qty_addl_comments'))

    article_to_process = db_manager.get_next_article_to_process()
    comment_thread_manager.set_article(article_to_process)

    if article_to_process is None:
        print("Fetching new articles from aggregator...")
        num_articles_returned = news_aggregator_manager.fetch_new_articles_into_db()
        if num_articles_returned == 0:
            print("No new articles returned from aggregator. Exiting...")
            return None
        print("New articles fetched: ", num_articles_returned)
        article_to_process = db_manager.get_next_article_to_process()

    print("     Article: ", article_to_process.title)
    print("url      :", article_to_process.url)

    db_manager.update_process_time(article_to_process)

    if article_to_process.scraped_website_content is None or len(article_to_process.scraped_website_content) == 0:
        print("No content found. Scraping article...")

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

    summary_model = ai_manager.return_model_by_name(summary_model_name)
    summary_prompt, prompt_keywords = generate_summary_prompt(article_to_process.scraped_website_content)
    print("    summary_prompt: ", summary_prompt, "\n")
    summary, flavors = ai_manager.fetch_inference(summary_model, summary_prompt)
    summary = extract_pure_text_from_raw_html(summary)

    if summary is None or len(summary) == 0:
        print("No summary generated. Exiting...")
        return

    comment_thread_manager.add_comment(0, summary, summary_model.get("polite_name", "anonymous llm"), prompt_keywords + " | " + flavors, datetime.now() )
    comment_history.append(summary)

    first_comment_model = ai_manager.return_model_by_name(first_comment_model_name)
    first_comment_prompt, prompt_keywords = generate_first_comment_prompt(summary)
    print("    first_comment_prompt: ", first_comment_prompt, "\n")
    first_comment, flavors = ai_manager.fetch_inference(first_comment_model, first_comment_prompt)

    if first_comment is None or len(first_comment) == 0:
        print("No first comment generated. Exiting...")
        return

    comment_thread_manager.add_comment(0, first_comment, first_comment_model.get("polite_name", "anonymous llm"), prompt_keywords  + " | " +  flavors, datetime.now() )
    comment_history.append(extract_pure_text_from_raw_html(first_comment))

    for _ in range(1, qty_addl_comments):
        parent_index = random.randint(0, int(comment_thread_manager.get_comments_length() * continuity_multiplier))
        parent_index = min(parent_index, comment_thread_manager.get_comments_length() - 1)
        parent_comment = comment_thread_manager.get_comment(parent_index)["comment"]

        temp_loop_comment_model = ai_manager.return_model_by_name(loop_comment_model_name)

        loop_comment_prompt, prompt_keywords = generate_loop_prompt(summary, parent_comment)
        print("    loop_comment_prompt: ", loop_comment_prompt, "\n")

        loop_comment, flavors = ai_manager.fetch_inference(temp_loop_comment_model, loop_comment_prompt)

        if loop_comment is None or len(loop_comment) == 0:
            print("No loop comment generated. Skipping...")
            continue

        comment_thread_manager.add_comment(parent_index, loop_comment, temp_loop_comment_model.get("polite_name", "anonymous llm"), prompt_keywords  + " | " +  flavors, datetime.now())
        comment_history.append(extract_pure_text_from_raw_html(loop_comment))


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

    if config.getboolean('publishing_details', 'publish_to_pelican'):
        publish_pelican(config["publishing_details"])
        print("     Website published for: ", article_to_process.title)
    else:
        print("     Website not published. Pelican publishing disabled.")

    if config.getboolean('aws_s3_bucket_details', 'publish_to_s3'):
        number_of_files_pushed = upload_directory_to_s3(config["aws_s3_bucket_details"], config["publishing_details"]["local_publish_path"])
        print(number_of_files_pushed)
    else:
        print("     Website not pushed. S3 publishing disabled.")

    print("     Done. Elapsed time:", comment_thread_manager.get_duration())

if __name__ == "__main__":
    main()
