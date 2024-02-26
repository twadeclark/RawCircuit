from abc import ABC, abstractmethod
# from datetime import datetime


class BaseDBManager(ABC):

    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def article_exists(self, url):
        pass

    @abstractmethod
    def save_article(self, article_data):
        pass

    @abstractmethod
    def get_random_article(self):
        pass

    @abstractmethod
    def get_next_article_to_scrape(self):
        pass

    @abstractmethod
    def get_next_article_to_process(self):
        pass

    @abstractmethod
    def update_scrape_time(self, article):
        pass

    @abstractmethod
    def update_process_time(self, article):
        pass

    @abstractmethod
    def update_scraped_website_content(self, article):
        pass

    @abstractmethod
    def get_models_with_none_success(self):
        pass

    @abstractmethod
    def insert_model_record(self, model_name):
        pass

    @abstractmethod
    def update_model_record(self, model_name, success, disposition):
        pass

    @abstractmethod
    def update_model_record_template(self, model_name, template):
        pass

    @abstractmethod
    def get_model_name_list_by_list_of_model_names(self, list_of_model_names):
        pass

    @abstractmethod
    def only_insert_model_into_database_if_not_already_there(self, model_name):
        pass
