from aggregators.news_aggregator_manager import NewsAggregatorManager
from contributors.ai_manager import AIManager
from instruction_generator import generate_instructions

GET_NEW_ARTICLE = False # for testing purposes

def main():
    manager = NewsAggregatorManager()

    if GET_NEW_ARTICLE:
        article = manager.get_article()
    else:
        article = manager.get_random_article()

    print("\nArticle:")
    print(article.content)

    if article is None:
        print("No articles found.")
        return

    ai_manager = AIManager()
    provider_name = "OpenAI_interface"

    summary = ai_manager.get_summary(provider_name, article.content)
    print("     AI Summary:")
    print(summary, "\n")

    comment = summary

    for _ in range(0, 10):
        instructions = generate_instructions()
        print("     Instructions: ", instructions)

        system_content = instructions
        user_content = comment

        comment = ai_manager.generate_comment(provider_name, user_content, system_content)

        comment_temp = "\n".join([line for line in comment.split("\n") if not line.startswith("#")])
        if comment_temp != comment:
            comment = comment_temp

        comment = comment.strip()

        if comment is None or len(comment) == 0:
            print("No comment generated. Skipping...")
            comment = summary
        else:
            print("     AI Comment:")
            print(comment)

        print()

if __name__ == "__main__":
    main()
