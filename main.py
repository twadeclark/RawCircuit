from article_manager.article_manager import ArticleManager


def main():
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

    print ( "SUCCESS: \t" + \
            f"article_id: {article_manager.article_to_process.id} \t" + \
            final_results + \
            f"Elapsed time: {article_manager.comment_thread_manager.get_duration()}\n")


if __name__ == "__main__":
    main()
