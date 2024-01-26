import configparser
import os
import random
from datetime import datetime, timezone
import time
from aggregators.news_aggregator_manager import NewsAggregatorManager
from comment_thread_manager import CommentThreadManager
from content_loaders.scraper import extract_raw_html_from_url, extract_text_from_html
# from content_loaders.scraper import extract_text_from_url
from contributors.ai_manager import AIManager
# from database.db_manager import DBManager
from instruction_generator import generate_instructions
from output_formatter.markdown_formatter import format_to_markdown
from vocabulary.news_search import SearchTerms
# from content_loaders.scraper import extract_text_from_html, get_page_source_from_url

GET_NEW_ARTICLE = False # for testing purposes

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    article_freshness = int(config.get('general_configurations', 'article_freshness'))

    # select the article with the lowest rec_order from the list of added_timestamp most recent articles that have scraped_timestamp=none and processed_timestamp=none
    news_aggregator_manager = NewsAggregatorManager()
    article_to_process = news_aggregator_manager.get_next_article_to_process()

    # if it's more than article_freshness seconds old, get new articles

    # print("datetime.now()                    :", datetime.now())
    # print("article_to_process.added_timestamp:", article_to_process.added_timestamp)
    # print("datetime.now(timezone.utc)        :", datetime.now(timezone.utc))


    # #this_is_now = current date and time in pacific time zone
    # this_is_now = datetime.now(timezone.utc).astimezone()
    # print("this_is_now                       :", this_is_now)
    # print("this_is_now - article_to_process.added_timestamp:", this_is_now - article_to_process.added_timestamp)
    # print("this_is_now - article_to_process.added_timestamp).total_seconds():", (this_is_now - article_to_process.added_timestamp).total_seconds())


    
    this_is_now = datetime.now()



    if article_to_process is None or (datetime.now(timezone.utc) - article_to_process.added_timestamp).total_seconds() > article_freshness:
        # https://newsapi.org/docs/endpoints/everything
            # we can put multiple search terms in the same call
            # (artifical and intelligence) or (machine and learning) or (ChatGPT) or (LLM) or (robot) or (computer vision)
            # this needs to be tested
        # we get back 100 articles so store them all in the database. the order is important
        # select the lowest rec_order article from the list
        print("loading new articles into database...")
        news_aggregator_manager.load_new_articles_into_db()

    article_to_process = news_aggregator_manager.get_next_article_to_process()

    if article_to_process is None:
        print("No article to process. Exiting...")
        return

    # update scrape time
    news_aggregator_manager.update_scrape_time(article_to_process)

    # get page source
    article_to_process.scraped_website_content, success = extract_raw_html_from_url(article_to_process.url)

    # store the scraped content in the database
    news_aggregator_manager.update_scraped_website_content(article_to_process)

    # if extract_text_from_url failed, capture the error and store it in the database, quit
    if not success:
        print("Error scraping article. Exiting...")
        return

    # update process time
    news_aggregator_manager.update_process_time(article_to_process)


    # get tag cloud and category
    text_from_page = extract_text_from_html(article_to_process.scraped_website_content)
    search_terms = SearchTerms()
    # tags = search_terms.find_tags_in_article(text_from_page)

    # sort tags by count, descending, and truncate to 5
    # tags.sort(key=lambda x: x[1], reverse=True)
    # tags = tags[:5]


    category, tags = search_terms.categorize_article_all_tags(text_from_page)


    print("url      :", article_to_process.url)
    print("category :", category)
    print("tags     :", tags)

    
    



    return



    # process article adding comments






    continuity_multiplier = float(config.get('general_configurations', 'continuity_multiplier'))
    qty_addl_comments = int(config.get('general_configurations', 'qty_addl_comments'))
    # no_article_retries = int(config.get('general_configurations', 'no_article_retries'))

    ai_manager = AIManager()
    search_terms = SearchTerms()
    ai_manager.choose_random_provider()
    # article = None


    article = article_to_process


    # if GET_NEW_ARTICLE:
    #     while article is None and no_article_retries > 0:
    #         random_category, random_term = search_terms.get_random_term()
    #         print("     random_category:", random_category, " random_term:", random_term)
    #         article = manager.get_article(random_term)
    #         no_article_retries -= 1
    # else:
    #     article = manager.get_random_article()
    #     print("\n     Database article:", article.title)

    # if article is None:
    #     print("No article found. Exiting...")
    #     return

    print("     Article:", article.title)
    print(article.content)

    tags = search_terms.find_tags_in_article(article)
    print("     tags:", tags)

    comment_thread_manager = CommentThreadManager(article, random_category, tags)

    # summary and first comment belong to same ai

    summary = ai_manager.get_summary(article.content)
    print("     AI Summary:")
    print(summary, "\n")

    comment_thread_manager.add_comment(0, summary, ai_manager.get_model_polite_name(), datetime.now() )

    instructions = generate_instructions()
    print("     1st Comment Instructions: ", instructions)
    comment = ai_manager.generate_comment(summary, instructions)

    print("     1st Comment:")
    print(comment, "\n")

    comment_thread_manager.add_comment(0, comment, ai_manager.get_model_polite_name(), datetime.now() )

    for _ in range(2, 2 + qty_addl_comments):
        ai_manager.choose_random_provider()
        instructions = generate_instructions()
        print("     Instructions: ", instructions)

        parent_index = random.randint(0, int(comment_thread_manager.get_comments_length() * continuity_multiplier))
        parent_index = min(parent_index, comment_thread_manager.get_comments_length() - 1)
        parent_comment = comment_thread_manager.get_comment(parent_index)["comment"]

        comment = ai_manager.generate_comment(parent_comment, instructions)
        comment = comment.strip()

        comment_temp = "\n".join([line for line in comment.split("\n") if not line.startswith("#")])
        if comment_temp != comment:
            comment = comment_temp

        if comment is None or len(comment) == 0:
            print("No comment generated. Skipping...")
            comment = summary
        else:
            comment_thread_manager.add_comment(parent_index, comment, ai_manager.get_model_polite_name(), datetime.now() )
            print("     AI Comment:")
            print(comment)

        print()





    formatted_post = format_to_markdown(article, comment_thread_manager)
    print("Post sucessfully formatted. ", len(formatted_post), "characters")
    # print(formatted_post)

    unique_seconds = int(time.time())

    base_path = config.get('general_configurations', 'completed_articles_path')
    file_name = "formatted_post_" + str(unique_seconds) + ".md"
    file_path = os.path.join(base_path, file_name)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(formatted_post)
    print("Formatted post saved to:", file_path)

if __name__ == "__main__":
    main()
