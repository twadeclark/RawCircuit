import configparser
import os
import random
from datetime import datetime
import time
from aggregators.news_aggregator_manager import NewsAggregatorManager
from comment_thread_manager import CommentThreadManager
from contributors.ai_manager import AIManager
from instruction_generator import generate_instructions_wrapping_input
from output_formatter.markdown_formatter import format_to_markdown
from vocabulary.news_search import SearchTerms

GET_NEW_ARTICLE = False # for testing purposes

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    continuity_multiplier = float(config.get('general_configurations', 'continuity_multiplier'))
    qty_addl_comments = int(config.get('general_configurations', 'qty_addl_comments'))
    completed_articles_path = config.get('general_configurations', 'completed_articles_path')

    news_aggregator_manager = NewsAggregatorManager("NewsApiOrgNews")
    article_to_process = news_aggregator_manager.get_next_article_to_process()

    if article_to_process is None:
        print("No article to process. Exiting...")
        return

    print("     Article:", article_to_process.title)

    news_aggregator_manager.update_process_time(article_to_process)
    search_terms = SearchTerms()
    article_to_process.unstored_category, article_to_process.unstored_tags = search_terms.categorize_article_all_tags(article_to_process.scraped_website_content)

    print("url      :", article_to_process.url)
    print("category :", article_to_process.unstored_category)
    print("tags     :", article_to_process.unstored_tags)

    ai_manager = AIManager()
    ai_manager.choose_random_provider()
    summary = ai_manager.get_summary(article_to_process.scraped_website_content)
    summary = summary.strip()

    if summary is None or len(summary) == 0:
        print("No summary generated. Exiting...")
        return

    print("     AI Summary: ", summary, "\n")

    comment_thread_manager = CommentThreadManager(article_to_process)
    comment_thread_manager.add_comment(0, summary, ai_manager.get_model_polite_name(), datetime.now() )

    # first comment belongs to summary ai
    instructions = generate_instructions_wrapping_input(article_to_process.description, summary)
    print("     1st Comment Instructions: ", instructions)
    comment = ai_manager.generate_comment_preformatted_message_streaming(instructions)
    comment = comment.strip()

    if comment is None or len(comment) == 0:
        print("No 1st Comment generated. Exiting...")
        return

    print("     1st Comment:",comment, "\n")

    comment_thread_manager.add_comment(0, comment, ai_manager.get_model_polite_name(), datetime.now() )

    for _ in range(2, 2 + qty_addl_comments):
        ai_manager.choose_random_provider()

        parent_index = random.randint(0, int(comment_thread_manager.get_comments_length() * continuity_multiplier))
        parent_index = min(parent_index, comment_thread_manager.get_comments_length() - 1)
        parent_comment = comment_thread_manager.get_comment(parent_index)["comment"]

        instructions = generate_instructions_wrapping_input(article_to_process.description, parent_comment)
        print("     Instructions: ", instructions)
        comment = ai_manager.generate_comment_preformatted_message_streaming(instructions)
        comment = comment.strip()

        if comment is None or len(comment) == 0:
            print("No comment generated. Stopping...")
            return

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

if __name__ == "__main__":
    main()
