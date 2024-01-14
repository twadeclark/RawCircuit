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
    print("\nAI Summary:")
    print(summary)


    for _ in range(0, 100):
        instructions = generate_instructions()

        print("\nInstructions: ", instructions)

        comment = ai_manager.generate_comment(provider_name, summary, instructions)
        comment = comment.strip()

        if comment is None or len(comment) == 0:
            print("No comment generated. Rerunning...")
        else:
            print("AI Comment:")
            print(comment)
            # summary = comment


if __name__ == "__main__":
    main()
