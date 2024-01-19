import datetime
import random
from aggregators.news_aggregator_manager import NewsAggregatorManager
from comment_thread_manager import CommentThreadManager
from contributors.ai_manager import AIManager
from instruction_generator import generate_instructions
from output_formatter.markdown_formatter import format_to_markdown

GET_NEW_ARTICLE = False # for testing purposes

def main():
    manager = NewsAggregatorManager()
    ai_manager = AIManager()
    ai_manager.choose_random_provider()

    if GET_NEW_ARTICLE:
        article = manager.get_article()
    else:
        article = manager.get_random_article()

    if article.content is None:
        print("No article found. Exiting...")
        return

    comment_thread_manager = CommentThreadManager(article)

    print("\nArticle:")
    print(article.content)

    # summary and first comment belong to same ai

    summary = ai_manager.get_summary(article.content)
    print("     AI Summary:")
    print(summary, "\n")

    comment_thread_manager.add_comment(0, summary, ai_manager.get_model_polite_name(), datetime.datetime.now() )

    instructions = generate_instructions()
    print("     1st Comment Instructions: ", instructions)
    comment = ai_manager.generate_comment(summary, instructions)

    print("     1st Comment:")
    print(comment, "\n")

    comment_thread_manager.add_comment(0, comment, ai_manager.get_model_polite_name(), datetime.datetime.now() )

    for loop in range(2, 10):
        ai_manager.choose_random_provider()
        instructions = generate_instructions()
        print("     Instructions: ", instructions)

        parent_index = random.randint(0, comment_thread_manager.get_comments_length() - 1)
        parent_comment = comment_thread_manager.get_comment(parent_index)["comment"]

        comment = ai_manager.generate_comment(parent_comment, instructions)
        comment = comment.strip()

        # comment += "parent_index. " + str(parent_index) + "\n"

        comment_temp = "\n".join([line for line in comment.split("\n") if not line.startswith("#")])
        if comment_temp != comment:
            comment = comment_temp

        if comment is None or len(comment) == 0:
            print("No comment generated. Skipping...")
            comment = summary
        else:
            comment_thread_manager.add_comment(parent_index, comment, ai_manager.get_model_polite_name(), datetime.datetime.now() )
            print("     AI Comment:")
            print(comment)

        print()

    formatted_post = format_to_markdown(article, comment_thread_manager)
    print("Formatted Post:")
    print(formatted_post)

    # save formatted_post to a file at "C:\Users\twade\projects\yoursite\content"
    file_path = r"C:\Users\twade\projects\yoursite\content\formatted_post.md"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(formatted_post)
    print("Formatted post saved to:", file_path)

if __name__ == "__main__":
    main()
