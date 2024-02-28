import configparser
from datetime import datetime
import logging
from article_manager.article_manager import ArticleManager
from log_config import setup_logging
setup_logging()

def main():
    logger = logging.getLogger(__name__) 
    logger.critical("\n-- -- -- -- -- -- -- -- -- -- -- Starting main() -- -- -- -- -- -- -- -- -- -- --")

    config = configparser.ConfigParser()
    config.read('config.ini')
    articles_total_qty = int(config['general_configurations']['articles_total_qty'])
    completed_articles = 0

    for article_counter in range(1, int(articles_total_qty) + 1):
        logger.warning("    Starting article %d of %d", article_counter, articles_total_qty)

        article_manager = ArticleManager(config)
        article_manager.load_news_article()

        if article_manager.model_info_from_config["name"] or article_manager.model_info_from_config["interface"] == "LocalOpenAIInterface":
            article_manager.get_summary_model_defined()
        else:
            article_manager.get_summary_find_model()

        if not article_manager.article_to_process.summary:
            logger.info("    No summary returned for article %d. Skipping.", article_counter)
            continue

        article_manager.add_summary_to_comment_thread_manager()

        first_comment = article_manager.fetch_and_add_first_comment()
        if not first_comment:
            logger.info("    No first comment returned for article %d. Skipping.", article_counter)
            continue

        article_manager.generate_additional_comments()
        article_manager.format_article_into_markdown()
        completed_articles += 1

    logger.warning("    Done with loop.")

    article_manager.publish_by_pelican()
    article_manager.push_to_S3()

    logger.critical ("SUCCESS: Completed %d articles out of %d attempts.\n", completed_articles, articles_total_qty)
    print("end.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        main_logger = logging.getLogger(__name__)
        main_logger.critical("An terrible error occurred.")
        main_logger.exception(e)
