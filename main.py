import configparser
import os
import random
from datetime import datetime
import time
from aggregators.news_aggregator_manager import NewsAggregatorManager
from comment_thread_manager import CommentThreadManager
from content_loaders.scraper import full_sanitize_text
from contributors.ai_manager import AIManager
from instruction_generator import generate_brief_instructions, generate_instructions_wrapping_input
from output_formatter.markdown_formatter import format_to_markdown
from vocabulary.news_search import SearchTerms


def main():
    config = configparser.ConfigParser()
    search_terms = SearchTerms()
    ai_manager = AIManager()
    news_aggregator_manager = NewsAggregatorManager("NewsApiOrgNews")

    config.read('config.ini')
    continuity_multiplier = float(config.get('general_configurations', 'continuity_multiplier'))
    qty_addl_comments = int(config.get('general_configurations', 'qty_addl_comments'))
    completed_articles_path = config.get('general_configurations', 'completed_articles_path')


    article_to_process = news_aggregator_manager.get_next_article_to_process()

    if article_to_process is None:
        print("No article to process. Exiting...")
        return

    print("     Article:", article_to_process.title)

    news_aggregator_manager.update_process_time(article_to_process)
    article_to_process.unstored_category, article_to_process.unstored_tags = search_terms.categorize_article_all_tags(article_to_process.scraped_website_content)

    print("url      :", article_to_process.url)
    print("category :", article_to_process.unstored_category)
    print("tags     :", article_to_process.unstored_tags)

    # ai_manager.choose_random_ai_unit()
    ai_manager.choose_specific_ai_unit('Falconsai/text_summarization')

    summary = ai_manager.get_summary(article_to_process.scraped_website_content)

    if summary is None or len(summary) == 0:
        print("No summary generated. Exiting...")
        return
    print("     AI Summary: ", summary)

    comment_thread_manager = CommentThreadManager(article_to_process)
    comment_thread_manager.add_comment(0, summary, ai_manager.get_model_polite_name(), datetime.now() )

    for _ in range(1, qty_addl_comments):
        # ai_manager.choose_random_ai_unit()
        ai_manager.choose_specific_ai_unit('kanishka/smolm-autoreg-bpe-counterfactual-babylm-pipps_and_keys_to_it_all_removal-1e-3')

        parent_index = random.randint(0, int(comment_thread_manager.get_comments_length() * continuity_multiplier))
        parent_index = min(parent_index, comment_thread_manager.get_comments_length() - 1)
        parent_comment = comment_thread_manager.get_comment(parent_index)["comment"]

        # instructions = generate_instructions_wrapping_input(full_sanitize_text(article_to_process.description), full_sanitize_text(parent_comment))
        instructions = generate_brief_instructions()
        # print("     Instructions: ", instructions)

        # comment = ai_manager.generate_comment_preformatted_message_streaming(instructions)
        comment = ai_manager.generate_new_comment_from_summary_and_previous_comment(full_sanitize_text(instructions), full_sanitize_text(summary), full_sanitize_text(parent_comment))

        comment = full_sanitize_text(comment)
        if comment is None or len(comment) == 0:
            print("No comment generated. Skipping...")
            continue
        print()
        comment_thread_manager.add_comment(parent_index, comment, ai_manager.get_model_polite_name(), datetime.now() )

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
