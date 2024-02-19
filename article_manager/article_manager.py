import configparser
from datetime import datetime
import os
import random
import time

from aggregators.news_aggregator_manager import NewsAggregatorManager
from content_loaders import scraper
from contributors.ai_manager import AIManager
from contributors.huggingface_model_search import HuggingfaceModelSearch
from database.db_manager import DBManager
from error_handler import FatalError
from output_formatter.comment_thread_manager import CommentThreadManager
from output_formatter import markdown_formatter
from output_formatter import publish_pelican
from output_formatter import upload_directory_to_s3
from prompt_generator import instruction_generator
from vocabulary.news_search import SearchTerms


class ArticleManager:
    def __init__(self):
        self.comment_thread_manager = CommentThreadManager()
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.db_manager = DBManager(self.config['postgresql'])
        self.ai_manager = AIManager(self.config, self.db_manager)
        self.news_aggregator_manager = NewsAggregatorManager(self.config, self.db_manager, None) #TODO: news aggregator type should come from config
        self.search_terms = SearchTerms()
        self.hfms = HuggingfaceModelSearch(self.db_manager)
        self.model_info_from_config = {  "name"      : self.config.get('model_info', 'model_name'),
                        "interface" : self.config.get('model_info', 'interface'),
                        "max_tokens": self.config.getint('model_info', 'max_tokens')}
        print("model:", self.model_info_from_config)
        self.article_to_process = None

    def load_news_article(self):
        atp = self.db_manager.get_next_article_to_process()

        if not atp:
            print("Fetching new articles from aggregator...")
            num_articles_returned = self.news_aggregator_manager.fetch_new_articles_into_db()
            if not num_articles_returned:
                raise FatalError("No new articles returned from aggregator. Exiting...")
            print("New articles fetched: ", num_articles_returned)
            atp = self.db_manager.get_next_article_to_process()

        if not atp:
            raise FatalError("No article_to_process. Exiting...")

        self.article_to_process = atp
        self.db_manager.update_process_time(self.article_to_process)
        self.comment_thread_manager.set_article(self.article_to_process) #TODO: this seems like it should be set later, after the article has been processed

        if not self.article_to_process.scraped_website_content:
            self._fetch_and_set_scraped_website_content()

        # self.article_to_process.shortened_content = ' '.join(self.article_to_process.scraped_website_content.split()[:(max_tokens_for_summary // 2)])
        self.article_to_process.shortened_content = ' '.join(self.article_to_process.scraped_website_content.split()[:(self.model_info_from_config["max_tokens"] // 2)])
        print("    shortened_content: ", self.article_to_process.shortened_content, "\n")

        self.search_terms.categorize_article_add_tags(self.article_to_process)



    def get_summary_model_defined(self):
        self.article_to_process.model = self.model_info_from_config
        self.db_manager.only_insert_model_into_database_if_not_already_there(self.article_to_process.model["name"])
        self.article_to_process.summary, self.article_to_process.summary_dump = self.ai_manager.get_summary_and_record_model_results(self.article_to_process)

    def get_summary_find_model(self):
        cnt = int(self.config.get('general_configurations', 'number_of_models_to_try'))

        while not self.article_to_process.summary and cnt > 0:
            cnt -= 1

            model_name_temp = self.hfms.fetch_next_model_name_from_huggingface()
            if not model_name_temp:
                raise FatalError("No new models available from Huggingface. Exiting...")

            self.article_to_process.model = {   "name"      : model_name_temp,
                                                "interface" : self.model_info_from_config["interface"],
                                                "max_tokens": self.model_info_from_config["max_tokens"]
                                            }
            print("\nTrying model: ", self.article_to_process.model["name"])
            self.article_to_process.summary, self.article_to_process.summary_dump = self.ai_manager.get_summary_and_record_model_results(self.article_to_process) #TODO: clean up

    def add_summary_to_comment_thread_manager(self):
        self.comment_thread_manager.add_comment(0,
                                                self.article_to_process.summary,
                                                scraper.get_polite_name(self.article_to_process.model["name"]),
                                                "summary | summary",
                                                datetime.now()
                                                )

    def fetch_and_add_first_comment(self):
        first_comment_prompt, first_comment_prompt_keywords = instruction_generator.generate_first_comment_prompt(self.article_to_process.summary)
        print("    first_comment_prompt: ", first_comment_prompt)

        first_comment, first_comment_flavors = self.ai_manager.fetch_inference(self.article_to_process.model, first_comment_prompt)

        if not first_comment:
            raise FatalError("No first comment generated. Exiting...")

        self.comment_thread_manager.add_comment(0,
                                                first_comment,
                                                scraper.get_polite_name(self.article_to_process.model["name"]),
                                                first_comment_prompt_keywords  + " | " +  first_comment_flavors,
                                                datetime.now()
                                                )

    def generate_additional_comments(self):
        qty_addl_comments = int(self.config.get('general_configurations', 'qty_addl_comments'))
        continuity_multiplier = float(self.config.get('general_configurations', 'continuity_multiplier'))

        for _ in range(1, qty_addl_comments):
            parent_index = random.randint(0, int(self.comment_thread_manager.get_comments_length() * continuity_multiplier))
            parent_index = min(parent_index, self.comment_thread_manager.get_comments_length() - 1)
            parent_comment = self.comment_thread_manager.get_comment(parent_index)["comment"]

            loop_comment_prompt, prompt_keywords = instruction_generator.generate_loop_prompt(self.article_to_process.summary, parent_comment)
            print("\n    loop_comment_prompt: ", loop_comment_prompt)

            loop_comment, flavors = self.ai_manager.fetch_inference(self.article_to_process.model, loop_comment_prompt)
            if not loop_comment:
                print(f"No loop comment generated. model: {self.article_to_process.model["name"]} Skipping...")
                continue

            self.comment_thread_manager.add_comment(parent_index,
                                                    loop_comment,
                                                    scraper.get_polite_name(self.article_to_process.model["name"]),
                                                    prompt_keywords  + " | " +  flavors,
                                                    datetime.now()
                                                    )

    def format_and_publish(self):
        local_content_path = self.config.get('publishing_details', 'local_content_path')
        formatted_post = markdown_formatter.format_to_markdown(self.article_to_process, self.comment_thread_manager)
        print("\nPost sucessfully formatted. ", len(formatted_post), "characters")

        unique_seconds = int(time.time())
        file_name = "formatted_post_" + str(unique_seconds) + ".md"
        file_path = os.path.join(local_content_path, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(formatted_post)
        print("     Formatted post saved to:", file_path)

        pushed_to_pelican = "NOT published by Pelican. \t"
        if self.config.getboolean('publishing_details', 'publish_to_pelican'):
            publish_pelican.publish_pelican(self.config["publishing_details"])
            pushed_to_pelican = "PUBLISHED by Pelican. \t"

        published_to_s3 = "NOT pushed to S3. \t"
        if self.config.getboolean('aws_s3_bucket_details', 'publish_to_s3'):
            number_of_files_pushed = upload_directory_to_s3.upload_directory_to_s3(self.config["aws_s3_bucket_details"], self.config["publishing_details"]["local_publish_path"])
            published_to_s3 = f"PUSHED files to S3: {number_of_files_pushed} \t"

        return pushed_to_pelican + published_to_s3



    def _fetch_and_set_scraped_website_content(self):
        print("Content not in database. Scraping article...")

        self.db_manager.update_scrape_time(self.article_to_process)
        raw_html_from_url, fetch_success = scraper.fetch_raw_html_from_url(self.article_to_process.url)
        if not fetch_success:
            raise FatalError("Error with fetch_raw_html_from_url. Exiting...")

        self.article_to_process.scraped_website_content = scraper.extract_pure_text_from_raw_html(
                                                            scraper.get_article_text_based_on_content_hint(self.article_to_process.content, raw_html_from_url)
                                                            or raw_html_from_url)

        if not self.article_to_process.scraped_website_content:
            raise FatalError("Error scraping website content. Exiting...")

        self.db_manager.update_scraped_website_content(self.article_to_process)
