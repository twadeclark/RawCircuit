# main.py

# from article_fetcher import fetch_article
from comment_generator import generate_comment
from message_board_poster import post_comment
from aggregators import NewsAggregatorManager


def main():

    manager = NewsAggregatorManager()
    article = manager.get_article()
    print(article)


    # article = fetch_article()
    # print(f"Article fetched from: {article.aggregator}")
    # print(f"Article URL: {article.url}")
    # print(f"Article content: {article.content}")
    # comment = generate_comment(article.content)
    # post_comment(comment)

if __name__ == "__main__":
    main()
