# newsapiorg_news.py
from article import Article
from database.db_manager import DBManager
from .base_aggregator import NewsAggregator
import requests
from datetime import datetime, timedelta
import configparser

class newsapiorg_news(NewsAggregator):
    config = configparser.ConfigParser()
    config.read('config.ini')

    urlBaseAPI = config.get('NewsAPI', 'urlBaseAPI')
    q = config.get('NewsAPI', 'q')
    from_date = datetime.now() - timedelta(days=config.getint('NewsAPI', 'days_back'))
    sortBy = config.get('NewsAPI', 'sortBy')
    apiKey = config.get('NewsAPI', 'apiKey')

    def fetch_articles_as_JSON(self):
        params = {
            "q": self.q,
            "from": self.from_date,
            "sortBy": self.sortBy,
            "apiKey": self.apiKey
        }

        response = requests.get(self.urlBaseAPI, params=params)

        if response.status_code == 200: # The request was successful
            return response.json()  # Returns the JSON response as a Python dictionary
        else: # The request failed
            response.raise_for_status()

    def get_article(self) -> Article:
        try:
            articles_data = self.fetch_articles_as_JSON()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")

        articles_list = articles_data.get('articles', []) # Assuming articles_data contains the JSON response

        db_manager = DBManager()

        for articleItem in articles_list: # Each 'artarticleItemicle' is a dictionary containing details about a news article
            articleInstance = Article(
                self.urlBaseAPI,
                articleItem.get('source', {}).get('id'),
                articleItem.get('source', {}).get('name'),
                articleItem.get('author'),
                articleItem.get('title'),
                articleItem.get('description'),
                articleItem.get('url'),
                articleItem.get('urlToImage'),
                articleItem.get('publishedAt'),
                articleItem.get('content')
            )

            if db_manager.is_article_processed(articleInstance.url):
                continue
            else:
                db_manager.save_article(articleInstance)
                return articleInstance

        # No articles were found
        return None
