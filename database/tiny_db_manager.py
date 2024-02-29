from datetime import datetime
import inspect
from tinydb import TinyDB, Query
from article import Article

from database.base_db_manager import BaseDBManager

class TinyDBManager(BaseDBManager):

    def __init__(self, config):
        config_data = config["db_path"]
        self.db = TinyDB(config_data)

    def article_exists(self, url):
        ret_val = self.db.table("articles").search(Query().url == url)
        return ret_val

    def save_article(self, article_data):
        sig = inspect.signature(Article.__init__)
        param_names = set(sig.parameters.keys())

        article_dict = {
            key: value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value
            for key, value in article_data.__dict__.items()
            if key in param_names
        }

        highest_id = max((doc['id'] for doc in self.db.table('articles').all()), default=0)

        article_dict['id'] = highest_id + 1
        
        self.db.table("articles").insert(article_dict)

    def get_next_article_to_process(self):
        ArticleQuery = Query()

        query = (ArticleQuery.processed_timestamp == None)

        articles = self.db.table("articles").search(query)

        if not articles:
            return None

        articles.sort(key=lambda article: article["added_timestamp"])
        ret_val = Article(**articles[0])
        return ret_val

    def update_scrape_time(self, article):
        self.db.table('articles').update({"scraped_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, Query().id == article.id)

    def update_process_time(self, article):
        self.db.table('articles').update({"processed_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, Query().id == article.id)

    def update_scraped_website_content(self, article):
        self.db.table('articles').update({"scraped_website_content": article.scraped_website_content}, Query().id == article.id)


    def get_models_with_none_success(self):
        ret_val = self.db.table("model_records").search(Query().success == None)
        return ret_val

    def insert_model_record(self, model_name):
        self.db.table("model_records").insert({
            "model_name": model_name,
            "attempt_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "success": None,
            "disposition": None
        })

    def update_model_record(self, model_name, success, disposition):
        self.db.table("model_records").update({
            "success": success,
            "disposition": disposition
        }, Query().model_name == model_name)

    def get_model_name_list_by_list_of_model_names(self, list_of_model_names):
        ret_val = self.db.table("model_records").search(Query().model_name.one_of(list_of_model_names))
        return ret_val

    def only_insert_model_into_database_if_not_already_there(self, model_name):
        existing_record = self.db.table("model_records").search(Query().model_name == model_name)
        if not existing_record:
            self.insert_model_record(model_name)

    def get_first_model_with_none_success(self):
        ret_val = self.db.table("model_records").get(Query().success == None)
        return ret_val

    def get_first_model_name_with_none_success(self):
        ret_val = self.db.table("model_records").get(Query().success == None)
        if ret_val:
            return ret_val["model_name"]
        return None
