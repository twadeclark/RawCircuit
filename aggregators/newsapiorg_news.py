from datetime import datetime, timedelta
import configparser
import requests
from article import Article
from database.db_manager import DBManager
from .base_aggregator import NewsAggregator

class NewsApiOrgNews(NewsAggregator):
    config = configparser.ConfigParser()
    config.read('config.ini')

    urlBaseAPI = config.get('NewsAPI', 'urlBaseAPI')
    q = config.get('NewsAPI', 'q')
    from_date = datetime.now() - timedelta(days=config.getint('NewsAPI', 'days_back'))
    sortBy = config.get('NewsAPI', 'sortBy')
    apiKey = config.get('NewsAPI', 'apiKey')

    def fetch_articles_as_json(self):
        params = {
            "q": self.q,
            "from": self.from_date,
            "sortBy": self.sortBy,
            "apiKey": self.apiKey
        }

        response = requests.get(self.urlBaseAPI, params=params, timeout=5)

        if response.status_code == 200: # The request was successful
            return response.json()
        else: # The request failed
            response.raise_for_status()

    def get_article(self) -> Article:
        try:
            articles_data = self.fetch_articles_as_json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")

        articles_list = articles_data.get('articles', []) # presume articles_data contains the JSON response

        db_manager = DBManager()

        for article in articles_list:
            article_instance = Article(
                self.urlBaseAPI,
                article.get('source', {}).get('id'),
                article.get('source', {}).get('name'),
                article.get('author'),
                article.get('title'),
                article.get('description'),
                article.get('url'),
                article.get('urlToImage'),
                article.get('publishedAt'),
                article.get('content')
            )

            if db_manager.is_article_processed(article_instance.url):
                continue

            db_manager.save_article(article_instance)
            return article_instance

        # No articles were found
        return None
