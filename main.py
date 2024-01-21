import configparser
import os
import random
from datetime import datetime
import time
from aggregators.news_aggregator_manager import NewsAggregatorManager
from comment_thread_manager import CommentThreadManager
from contributors.ai_manager import AIManager
from instruction_generator import generate_instructions
from output_formatter.markdown_formatter import format_to_markdown
from vocabulary.news_search import SearchTerms

GET_NEW_ARTICLE = True # for testing purposes

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    continuity_multiplier = float(config.get('general_configurations', 'continuity_multiplier'))
    qty_addl_comments = int(config.get('general_configurations', 'qty_addl_comments'))

    manager = NewsAggregatorManager()
    ai_manager = AIManager()
    search_terms = SearchTerms()
    ai_manager.choose_random_provider()
    random_category, random_term = search_terms.get_random_term()

    if GET_NEW_ARTICLE:
        article = manager.get_article(random_term)
        print("     random_category:", random_category, " random_term:", random_term)
        print("     Article:", article.title)
        print(article.content)
    else:
        article = manager.get_random_article()
        print("\n     Database article:", article.title)

    if article is None:
        print("No article found. Exiting...")
        return

    tags = search_terms.find_tags_in_article(article)
    print("     tags:", tags)

    comment_thread_manager = CommentThreadManager(article, random_category, tags)

    # summary and first comment belong to same ai

    summary = ai_manager.get_summary(article.content)
    print("     AI Summary:")
    print(summary, "\n")

    comment_thread_manager.add_comment(0, summary, ai_manager.get_model_polite_name(), datetime.now() )

    instructions = generate_instructions()
    print("     1st Comment Instructions: ", instructions)
    comment = ai_manager.generate_comment(summary, instructions)

    print("     1st Comment:")
    print(comment, "\n")

    comment_thread_manager.add_comment(0, comment, ai_manager.get_model_polite_name(), datetime.now() )

    for _ in range(2, 2 + qty_addl_comments):
        ai_manager.choose_random_provider()
        instructions = generate_instructions()
        print("     Instructions: ", instructions)

        parent_index = random.randint(0, int(comment_thread_manager.get_comments_length() * continuity_multiplier))
        parent_index = min(parent_index, comment_thread_manager.get_comments_length() - 1)
        parent_comment = comment_thread_manager.get_comment(parent_index)["comment"]

        comment = ai_manager.generate_comment(parent_comment, instructions)
        comment = comment.strip()

        comment_temp = "\n".join([line for line in comment.split("\n") if not line.startswith("#")])
        if comment_temp != comment:
            comment = comment_temp

        if comment is None or len(comment) == 0:
            print("No comment generated. Skipping...")
            comment = summary
        else:
            comment_thread_manager.add_comment(parent_index, comment, ai_manager.get_model_polite_name(), datetime.now() )
            print("     AI Comment:")
            print(comment)

        print()

    formatted_post = format_to_markdown(article, comment_thread_manager)
    print("Post sucessfully formatted. ", len(formatted_post), "characters")
    # print(formatted_post)

    unique_seconds = int(time.time())

    base_path = config.get('general_configurations', 'completed_articles_path')
    file_name = "formatted_post_" + str(unique_seconds) + ".md"
    file_path = os.path.join(base_path, file_name)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(formatted_post)
    print("Formatted post saved to:", file_path)

if __name__ == "__main__":
    main()
