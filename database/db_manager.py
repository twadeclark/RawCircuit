# from datetime import datetime
# import psycopg2
# from psycopg2.extras import DictCursor
# from tinydb import TinyDB, Query
# from article import Article
from database.postgres_db_manager import PostgresDBManager
from database.tiny_db_manager import TinyDBManager


class DBManager:
    def __init__(self, config):
        # Read database type from config
        db_type = config["general_configurations"]["db_type"]

        if db_type == "TinyDB":
            self.conn = TinyDBManager(config["TinyDB"])
        elif db_type == "postgresql":
            self.conn = PostgresDBManager(config["postgresql"])
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def get_random_article(self):
        return self.conn.get_random_article()

    def get_next_article_to_scrape(self):
        return self.conn.get_next_article_to_scrape()

    def get_next_article_to_process(self):
        return self.conn.get_next_article_to_process()

    def update_scrape_time(self, article):
        self.conn.update_scrape_time(article)

    def update_process_time(self, article):
        self.conn.update_process_time(article)

    def update_scraped_website_content(self, article):
        self.conn.update_scraped_website_content(article)

    def get_models_with_none_success(self):
        return self.conn.get_models_with_none_success() 

    def insert_model_record(self, model_name):
        return self.conn.insert_model_record(model_name)

    def update_model_record(self, model_name, success, disposition):
        return self.conn.update_model_record(model_name, success, disposition)

    def update_model_record_template(self, model_name, template):
        return self.conn.update_model_record_template( model_name, template)

    def get_model_name_list_by_list_of_model_names(self, list_of_model_names):
        return self.conn.get_model_name_list_by_list_of_model_names(list_of_model_names)

    def only_insert_model_into_database_if_not_already_there(self, model_name):
        return self.conn.only_insert_model_into_database_if_not_already_there(model_name)

    def article_exists(self, url):
        return self.conn.article_exists(url)

    def save_article(self, article_data):
        return self.conn.save_article(article_data)
