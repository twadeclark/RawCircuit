import configparser
import datetime
import random
# from datetime import datetime, timezone
from aggregators.rss_feeder import RSSFeeder
from article import Article
from database.db_manager import DBManager
from content_loaders.scraper import extract_article, extract_last_integer, fetch_raw_html_from_url, extract_pure_text_from_raw_html
from .newsapiorg_news import NewsApiOrgNews

class NewsAggregatorManager: # we want to be able to choose an aggregator at random, or send in the name of the aggregator we want to use

    def __init__(self, aggregator_name=None):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.article_freshness = int(config.get('general_configurations', 'article_freshness'))
        self.db_manager = DBManager()
        self.aggregators = [ # Put the list of aggregators here
            NewsApiOrgNews(),
            RSSFeeder(),
        ]
        if aggregator_name is not None:
            self.aggregator = self.get_aggregator_by_name(aggregator_name)
        else:
            self.aggregator = random.choice(self.aggregators)

    # def get_next_article_to_process(self):
    #     article_to_process = None
    #     is_full_text_set = False
    #     while article_to_process is None:
    #         article_to_process = self.db_manager.get_next_article_to_process()

    #         if article_to_process is None: # or (datetime.now(timezone.utc) - article_to_process.added_timestamp).total_seconds() > self.article_freshness:
    #             print("Loading new articles into database...")
    #             #TODO: rotate through aggregators
    #             num_articles_returned = self.fetch_new_articles_into_db()
    #             if num_articles_returned == 0:
    #                 print("No new articles returned from aggregator. Exiting...")
    #                 return None
    #             else:
    #                 continue

    #         if article_to_process.scraped_timestamp is None:
    #             self.update_scrape_time(article_to_process)
    #             print(article_to_process.url)
    #             raw_html, success = fetch_raw_html_from_url(article_to_process.url)
    #             article_to_process.scraped_website_content = raw_html
    #             if not success:
    #                 print("Error scraping article. Continuing to next article...")
    #                 self.update_scraped_website_content(article_to_process)
    #                 self.update_process_time(article_to_process)
    #                 article_to_process = None
    #                 continue

    #             raw_text_extracted = extract_pure_text_from_raw_html(raw_html)
    #             if raw_text_extracted is None or len(raw_text_extracted) == 0:
    #                 self.update_scraped_website_content(article_to_process)
    #                 self.update_process_time(article_to_process)
    #                 article_to_process = None
    #                 continue

    #             is_full_text_set = self.get_article_text_based_on_content_hint(article_to_process, raw_html, raw_text_extracted)

    #         if article_to_process.scraped_website_content is None or len(article_to_process.scraped_website_content) < 220: #TODO: make this a config setting
    #             self.update_process_time(article_to_process)
    #             article_to_process = None

    #     if is_full_text_set:
    #         print("Full text set.")

    #     return article_to_process

    # def get_article_text_based_on_content_hint(self, article_to_process_content, raw_html):
    #     # this is all specific to only some news.api article content

    #     plus_chars = extract_last_integer(article_to_process_content)
    #     content_truncated = article_to_process_content.split('…', 1)[0]

    #     full_article = extract_article(raw_html, content_truncated, plus_chars)

    #     if full_article is None or len(full_article) == 0: # then we extract pure text and try again
    #         full_article = extract_article(extract_pure_text_from_raw_html(raw_html), extract_pure_text_from_raw_html(content_truncated), plus_chars)

    #     return full_article

    def get_aggregator_by_name(self, aggregator_name):
        for aggregator in self.aggregators:
            if aggregator.get_name() == aggregator_name:
                return aggregator
        return None

    def fetch_new_articles_into_db(self):
        articles = self.aggregator.fetch_articles()
        rec_order = 0
        for article in articles["articles"]:

            # check if article already exists in database
            # if so, skip it
            if self.db_manager.article_exists(article["url"]):
                continue

            # convert article to Article object, set any missing fields to None
            article = Article(
                None,
                self.aggregator.get_name(),
                article["source"]["id"],
                article["source"]["name"],
                article["author"],
                article["title"],
                article["description"],
                article["url"],
                article["urlToImage"],
                article["publishedAt"],
                article["content"],
                None,
                None,
                None,
                None,
                None
            )

            article.added_timestamp = datetime.datetime.now()
            article.rec_order = rec_order
            self.db_manager.save_article(article)
            rec_order += 1
        return rec_order

    def update_scrape_time(self, article):
        self.db_manager.update_scrape_time(article)

    def update_process_time(self, article):
        self.db_manager.update_process_time(article)

    def update_scraped_website_content(self, article):
        self.db_manager.update_scraped_website_content(article)
