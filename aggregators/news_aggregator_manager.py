import configparser
import random
# from datetime import datetime, timezone
from aggregators.rss_feeder import RSSFeeder
from database.db_manager import DBManager
from content_loaders.scraper import extract_article, extract_last_integer, fetch_raw_html_from_url, extract_text_from_html
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

    def get_next_article_to_process(self):
        article_to_process = None
        is_full_text_set = False
        while article_to_process is None:
            article_to_process = self.db_manager.get_next_article_to_process()

            if article_to_process is None: # or (datetime.now(timezone.utc) - article_to_process.added_timestamp).total_seconds() > self.article_freshness:
                print("Loading new articles into database...")
                #TODO: rotate through aggregators
                num_articles_returned = self.fetch_new_articles_into_db()
                if num_articles_returned == 0:
                    print("No articles returned from aggregator. Exiting...")
                    return None
                else:
                    continue

            if article_to_process.scraped_timestamp is None:
                self.update_scrape_time(article_to_process)
                print(article_to_process.url)
                raw_html, success = fetch_raw_html_from_url(article_to_process.url)
                article_to_process.scraped_website_content = raw_html
                if not success:
                    print("Error scraping article. Continuing to next article...")
                    self.update_scraped_website_content(article_to_process)
                    self.update_process_time(article_to_process)
                    article_to_process = None
                    continue

                raw_text_extracted = extract_text_from_html(raw_html)
                if raw_text_extracted is None or len(raw_text_extracted) == 0:
                    self.update_scraped_website_content(article_to_process)
                    self.update_process_time(article_to_process)
                    article_to_process = None
                    continue

                article_to_process.scraped_website_content = raw_text_extracted
                plus_chars = extract_last_integer(article_to_process.content)
                if plus_chars is not None:
                    content_truncated = article_to_process.content.split('…', 1)[0]
                    if content_truncated is not None and len(content_truncated) > 0:
                        full_article = extract_article(raw_html, content_truncated, plus_chars)
                        if full_article is not None and len(full_article) > 0:
                            article_to_process.scraped_website_content = full_article
                            is_full_text_set = True
                        else:
                            full_article = extract_article(extract_text_from_html(raw_html), extract_text_from_html(content_truncated), plus_chars)
                            if full_article is not None and len(full_article) > 0:
                                article_to_process.scraped_website_content = full_article
                                is_full_text_set = True

                article_to_process.scraped_website_content = extract_text_from_html(article_to_process.scraped_website_content)
                self.update_scraped_website_content(article_to_process)

            if article_to_process.scraped_website_content is None or len(article_to_process.scraped_website_content) < 220: #TODO: make this a config setting
                self.update_process_time(article_to_process)
                article_to_process = None

        if is_full_text_set:
            print("Full text set.")

        return article_to_process

    def get_aggregator_by_name(self, aggregator_name):
        for aggregator in self.aggregators:
            if aggregator.get_name() == aggregator_name:
                return aggregator
        return None

    def fetch_new_articles_into_db(self):
        articles = self.aggregator.fetch_articles()
        rec_order = 0
        for article in articles:
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
