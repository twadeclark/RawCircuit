# main.py

# from article_fetcher import fetch_article
from aggregators.news_aggregator_manager import NewsAggregatorManager
from comment_generator import generate_comment
from message_board_poster import post_comment


def main():
    manager = NewsAggregatorManager()
    article = manager.get_article()

    if article is None:
        print("No articles found.")
        return

    print(article)



if __name__ == "__main__":
    main()
