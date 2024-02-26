import configparser
from datetime import datetime
import os
import random
import time

import logging
from aggregators.news_aggregator_manager import NewsAggregatorManager
from article import Article
from content_loaders import scraper
from contributors.ai_manager import AIManager
from contributors.huggingface_model_search import HuggingfaceModelSearch
from database.db_manager import DBManager
from error_handler import FatalError
from output_formatter.comment_thread_manager import CommentThreadManager
from output_formatter import markdown_formatter
from output_formatter import publish_pelican
from output_formatter import upload_directory_to_s3
from prompt_generator.instruction_generator import InstructionGenerator
from vocabulary.news_search import SearchTerms

from log_config import setup_logging
setup_logging()


class ArticleManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.comment_thread_manager = CommentThreadManager()
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.db_manager = DBManager(self.config)
        self.instruction_generator =  InstructionGenerator(self.config.get('general_configurations', 'prompt_tier'))
        self.ai_manager = AIManager(self.config, self.db_manager, self.instruction_generator)
        self.news_aggregator_manager = NewsAggregatorManager(self.config, self.db_manager, None) #TODO: news aggregator type should come from config
        self.search_terms = SearchTerms()
        self.hfms = HuggingfaceModelSearch(self.db_manager)
        self.model_info_from_config = { "name"      : self.config.get('model_info', 'model_name'),
                                        "interface" : self.config.get('model_info', 'interface'),
                                        "max_tokens": self.config.getint('model_info', 'max_tokens')}
        self.logger.info("model_info_from_config: %s", self.model_info_from_config)
        self.article_to_process = None

    def load_news_article(self):
        if self.config.getboolean('article_selector', 'use_specific_article') and self.config.get('article_selector', 'specific_article_url'):
            atp =   Article(    id = None,
                                aggregator = "tmorganclark.com",
                                source_id = None,
                                source_name = "Thomas News Service",
                                author = self.config.get('article_selector', 'specific_article_author'),
                                title = self.config.get('article_selector', 'specific_article_title'),
                                description = None,
                                url = self.config.get('article_selector', 'specific_article_url'),
                                url_to_image= None,
                                published_at = datetime.now(),
                                content = None,
                                rec_order = 0,
                                added_timestamp = datetime.now(),
                                scraped_timestamp = None,
                                scraped_website_content = None,
                                processed_timestamp = None
                                )
        else:
            atp = self.db_manager.get_next_article_to_process()

            if not atp:
                self.logger.info("Fetching new articles from aggregator...")
                num_articles_returned = self.news_aggregator_manager.fetch_new_articles_into_db()
                if not num_articles_returned:
                    raise FatalError("No new articles returned from aggregator. Exiting...")
                self.logger.info("New articles fetched: %s", num_articles_returned)
                atp = self.db_manager.get_next_article_to_process()

        if not atp:
            raise FatalError("No article_to_process. Exiting...")

        self.article_to_process = atp
        self.db_manager.update_process_time(self.article_to_process)
        self.comment_thread_manager.set_article(self.article_to_process) #TODO: this seems like it should be set later, after the article has been processed

        if not self.article_to_process.scraped_website_content:
            if self.config.getboolean('article_selector', 'use_info_from_aggregator_instead_of_fetch'):
                self._use_info_from_aggregator_instead_of_fetch()
            else:
                self._fetch_and_set_scraped_website_content()

        shortened_content_tmp = ' '.join(self.article_to_process.scraped_website_content.split()[:(self.model_info_from_config["max_tokens"] // 2)])
        shortened_content_tmp = scraper.extract_pure_text_from_raw_html(shortened_content_tmp)
        self.article_to_process.shortened_content = shortened_content_tmp
        self.logger.info("    shortened_content: %s", self.article_to_process.shortened_content)


    def get_summary_model_defined(self):
        self.article_to_process.model = self.model_info_from_config
        self.ai_manager.get_and_set_summary_and_record_model_results(self.article_to_process)

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
            self.logger.info("\nTrying model: %s", self.article_to_process.model["name"])
            self.ai_manager.get_and_set_summary_and_record_model_results(self.article_to_process) #TODO: clean up

    def add_summary_to_comment_thread_manager(self):
        if not self.article_to_process.summary:
            raise FatalError("No summary generated. Exiting...")
        else:
            self.comment_thread_manager.add_comment(0,
                                                    self.article_to_process.summary,
                                                    scraper.get_polite_name(self.article_to_process.model["name"]),
                                                    # "summary | summary",
                                                    self.article_to_process.summary_prompt_keywords  + " | " +  self.article_to_process.summary_flavors,
                                                    datetime.now()
                                                    )

    def fetch_and_add_first_comment(self):
        first_comment_prompt, first_comment_prompt_keywords = self.instruction_generator.generate_first_comment_prompt(self.article_to_process.summary)
        self.logger.info("    first_comment_prompt: %s", first_comment_prompt)

        first_comment, first_comment_flavors = self.ai_manager.fetch_inference(self.article_to_process.model, first_comment_prompt, 0.0)

        if not first_comment:
            raise FatalError("No first comment generated. Exiting...")

        self.comment_thread_manager.add_comment(0,
                                                first_comment,
                                                scraper.get_polite_name(self.article_to_process.model["name"]),
                                                first_comment_prompt_keywords  + " | " +  first_comment_flavors,
                                                datetime.now()
                                                )

    def generate_additional_comments(self):
        continuity_multiplier = float(self.config.get('general_configurations', 'continuity_multiplier'))
        number_of_comments_between_min_max_temperature = int(self.config.get('general_configurations', 'number_of_comments_between_min_max_temperature'))
        max_comment_temperature = float(self.config.get('general_configurations', 'max_comment_temperature'))
        min_comment_temperature = float(self.config.get('general_configurations', 'min_comment_temperature'))
        temp_pct_increase = float( 1 / (number_of_comments_between_min_max_temperature + 2))
        temperature_increase = float(temp_pct_increase * (max_comment_temperature - min_comment_temperature))
        temperature = float(0.0 + temperature_increase)

        for _ in range(1, number_of_comments_between_min_max_temperature + 2):
            parent_index = random.randint(0, int(self.comment_thread_manager.get_comments_length() * continuity_multiplier))
            parent_index = min(parent_index, self.comment_thread_manager.get_comments_length() - 1)
            parent_comment = self.comment_thread_manager.get_comment(parent_index)["comment"]
            temperature += temperature_increase

            loop_comment_prompt, prompt_keywords = self.instruction_generator.generate_loop_prompt(self.article_to_process.summary, parent_comment)
            self.logger.info("\n    loop_comment_prompt: %s", loop_comment_prompt)

            loop_comment, flavors = self.ai_manager.fetch_inference(self.article_to_process.model, loop_comment_prompt, temperature)
            if not loop_comment:
                self.logger.info("No loop comment generated. model: %s Skipping...", self.article_to_process.model["name"])
                continue

            self.comment_thread_manager.add_comment(parent_index,
                                                    loop_comment,
                                                    scraper.get_polite_name(self.article_to_process.model["name"]),
                                                    prompt_keywords  + " | " +  flavors,
                                                    datetime.now()
                                                    )

    def format_and_publish(self):
        self.search_terms.categorize_article_add_tags(self.article_to_process)

        local_content_path = self.config.get('publishing_details', 'local_content_path')
        formatted_post = markdown_formatter.format_to_markdown(self.article_to_process, self.comment_thread_manager)
        self.logger.info("\nPost sucessfully formatted. %s characters \t(%s)", len(formatted_post), self.article_to_process.title)

        unique_seconds = int(time.time())
        file_name = "formatted_post_" + str(unique_seconds) + ".md"
        file_path = os.path.join(local_content_path, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(formatted_post)
        self.logger.info("     Formatted post saved to: %s", file_path)

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
        self.logger.info("Content not in database. Scraping article...")

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

    def _use_info_from_aggregator_instead_of_fetch(self):
        self.logger.info("Using info from aggregator instead of fetch..")
        self.db_manager.update_scrape_time(self.article_to_process)

        title_clause = source_name_clause = author_clause = description_clause = content_clause = ""

        if self.article_to_process.title:
            title_clause = f"The title of this article is {self.article_to_process.title}. "

        if self.article_to_process.source_name:
            source_name_clause = f"The news source is {self.article_to_process.source_name}. "

        if self.article_to_process.author:
            author_clause = f"The author is {self.article_to_process.author}. "

        if self.article_to_process.description:
            description_clause = scraper.extract_pure_text_from_raw_html(scraper.quick_clean(self.article_to_process.description))

        if self.article_to_process.content:
            content_clause = scraper.extract_pure_text_from_raw_html(scraper.quick_clean(self.article_to_process.content))

        fake_content = f"{title_clause}{source_name_clause}{author_clause}{description_clause}{content_clause}"
        self.article_to_process.scraped_website_content = fake_content
        self.logger.info("fake_content: %s", fake_content)

        if not self.article_to_process.scraped_website_content:
            raise FatalError("Error assembling fake content. Exiting...")

        self.db_manager.update_scraped_website_content(self.article_to_process)
