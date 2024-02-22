from datetime import datetime
import inspect
from tinydb import TinyDB, Query
from article import Article

from database.base_db_manager import BaseDBManager

class TinyDBManager(BaseDBManager):

    def __init__(self, config):
        # Initialize TinyDB connection using config data
        config_data = config["db_path"]
        self.db = TinyDB(config_data)

    def article_exists(self, url):
        # Use TinyDB query syntax to check if article exists
        ret_val = self.db.table("articles").search(Query().url == url)
        return ret_val

    def save_article(self, article_data):
        # Get parameter names from Article constructor
        sig = inspect.signature(Article.__init__)
        param_names = set(sig.parameters.keys())

        # Convert Article object to dictionary, handling datetime objects
        article_dict = {
            key: value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime) else value
            for key, value in article_data.__dict__.items()
            if key in param_names  # Only include parameters that appear in Article constructor
        }

        # Get the highest ID currently in the database
        highest_id = max((doc['id'] for doc in self.db.table('articles').all()), default=0)

        # Assign the next ID to the new record
        article_dict['id'] = highest_id + 1
        
        # Insert the JSON-compatible dictionary
        self.db.table("articles").insert(article_dict)


    def get_random_article(self): # NOT ACCESSED, slated for removal
        # Use TinyDB's rand() function for random selection
        article = self.db.table("articles").random()
        ret_val = Article(**article) if article else None
        return ret_val

    def get_next_article_to_scrape(self): # NOT ACCESSED, slated for removal
        # Construct query to find next article for scraping
        query = Query()
        query.scraped_timestamp = None
        query.processed_timestamp = None
        query.scraped_website_content = None
        article = self.db.table("articles").search(query).sort(by="added_timestamp", ascending=True).first()
        ret_val = Article(**article) if article else None
        return ret_val


    def get_next_article_to_process(self):
        # Initialize Query object
        ArticleQuery = Query()

        # Construct query to find next article for processing
        # This checks for documents where 'processed_timestamp' does not exist or is None
        query = (ArticleQuery.processed_timestamp == None)

        # Get matching articles and check for empty result
        articles = self.db.table("articles").search(query)

        if not articles:
            # Handle the case where no articles match the query (all are processed)
            return None

        # Sort and return the first article if any exist
        articles.sort(key=lambda article: article["added_timestamp"])
        ret_val = Article(**articles[0])
        return ret_val

    def update_scrape_time(self, article):
        # Update scraped_timestamp for the article
        self.db.table('articles').update({"scraped_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, Query().id == article.id)

    def update_process_time(self, article):
        # Update processed_timestamp for the article
        # self.db.table('articles').update({"processed_timestamp": datetime.now()}, Query().id == article.id)
        self.db.table('articles').update({"processed_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, Query().id == article.id)

    def update_scraped_website_content(self, article):
        # Update scraped_website_content for the article
        self.db.table('articles').update({"scraped_website_content": article.scraped_website_content}, Query().id == article.id)

    def get_models_with_none_success(self):
        # Use TinyDB query to find models with no success value
        ret_val = self.db.table("model_records").search(Query().success == None)
        return ret_val

    def insert_model_record(self, model_name):
        # Insert new model record with current timestamp
        self.db.table("model_records").insert({
            "model_name": model_name,
            "attempt_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "success": None,
            "disposition": None
        })

    def update_model_record(self, model_name, success, disposition):
        # Update success and disposition for the model
        self.db.table("model_records").update({
            "success": success,
            "disposition": disposition
        }, Query().model_name == model_name)

    def get_model_name_list_by_list_of_model_names(self, list_of_model_names):
        # Search for models matching names in the list
        ret_val = self.db.table("model_records").search(Query().model_name.one_of(list_of_model_names))
        return ret_val

    def only_insert_model_into_database_if_not_already_there(self, model_name):
        # Check if model already exists using search
        existing_record = self.db.table("model_records").search(Query().model_name == model_name)
        if not existing_record:
            # Insert new record if not found
            self.insert_model_record(model_name)
