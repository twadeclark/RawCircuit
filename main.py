from aggregators.news_aggregator_manager import NewsAggregatorManager
from comment_generator import generate_comment
from contributors import ai_manager
from message_board_poster import post_comment
# from contributors.ai_manager import AIManager


def main():
    manager = NewsAggregatorManager()
    article = manager.get_article()

    if article is None:
        print("No articles found.")
        return

    print(article)

    instructions = "Some instructions"
    provider_name = "local"  # or "remote_api1", "remote_api2"
    
    comment = ai_manager.get_comment(provider_name, article, instructions)
    print(comment)



if __name__ == "__main__":
    main()
