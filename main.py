import logging
from article_manager.article_manager import ArticleManager
from log_config import setup_logging
setup_logging()

def main():
    logger = logging.getLogger(__name__)
    logger.critical("Starting main()")

    import os
    print("Current Working Directory:", os.getcwd())

    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        if 'NewsAPI' in config:
            # Access the configuration
            news_api = config['NewsAPI']
            print(f"news_api = {news_api}")

            news_api2 = config.get('NewsAPI')
            print(f"news_api2 = {news_api2}")

            news_api3 = config['NewsAPI']['apiKey']
            print(f"news_api3 = {news_api3}")

        else:
            # Handle the case where 'NewsAPI' section is missing
            print("The 'NewsAPI' section is missing from the config.ini file.")
    except Exception as e:
        print(f"1. An error occurred: {e}")

    try:
        print(f"config = {config}")
    except Exception as e:
        print(f"2. An error occurred: {e}")

    print("here!")


    article_manager = ArticleManager()

    article_manager.load_news_article()

    if article_manager.model_info_from_config["name"] or article_manager.model_info_from_config["interface"] == "LocalOpenAIInterface":
        article_manager.get_summary_model_defined()
    else:
        article_manager.get_summary_find_model()

    article_manager.add_summary_to_comment_thread_manager()
    article_manager.fetch_and_add_first_comment()
    article_manager.generate_additional_comments()
    final_results = article_manager.format_and_publish()

    logger.critical (   "SUCCESS: \t" + \
                        f"article_id: {article_manager.article_to_process.id} \t" + \
                        final_results + \
                        f"Elapsed time: {article_manager.comment_thread_manager.get_duration()}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        main_logger = logging.getLogger(__name__)
        main_logger.critical("An terrible error occurred.")
        main_logger.exception(e)
        raise e
