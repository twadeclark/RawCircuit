from aggregators.news_aggregator_manager import NewsAggregatorManager
from contributors.ai_manager import AIManager

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


    instructions = "You are a humurous poet. You respond in short witty poems."
    print("\nInstructions:")
    print(instructions)

    comment = ai_manager.generate_comment(provider_name, summary, instructions)
    print("\nAI Comment:")
    print(comment)
    print("\n")


if __name__ == "__main__":
    main()
