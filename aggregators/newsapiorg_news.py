from datetime import datetime, timedelta
import configparser
import random
import requests
from newsapi import NewsApiClient
from article import Article
from database.db_manager import DBManager
from .base_aggregator import NewsAggregator

class NewsApiOrgNews(NewsAggregator):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.from_date = datetime.now() - timedelta(days=config.getint('NewsAPI', 'days_back'))
        self.sort_by = config.get('NewsAPI', 'sortBy')
        self.api_key = config.get('NewsAPI', 'apiKey')
        self.newsapi = NewsApiClient(api_key=self.api_key)

    def get_articles(self):
        query_term = "" #TODO: get this from the search terms
        return random.choice(self.fetch_methods())(query_term)

    def fetch_methods(self):
        return [
            self.fetch_top_headlines,
            self.fetch_everything_headlines
        ]

    def fetch_top_headlines(self, query_term):
        top_headlines = self.newsapi.get_top_headlines( q=f"{query_term}",
                                                        category='technology',
                                                        language='en')
        return top_headlines

    def fetch_everything_headlines(self, query_term):
        all_articles = self.newsapi.get_everything( q=f"{query_term}",
                                                    from_param=self.from_date,
                                                    sort_by='relevancy',
                                                    language='en')
        return all_articles

    def get_article(self, query_term) -> Article:
        # we try to get the top headlines first, if that fails we try to get everything
        try:
            articles_data = self.fetch_top_headlines(query_term)
        except requests.RequestException as e:
            print(f"An error occurred (fetch_top_headlines): {e}")

        articles_list = articles_data.get('articles', []) # presume articles_data contains the JSON response

        if len(articles_list) == 0:
            try:
                articles_data = self.fetch_everything_headlines(query_term)
                articles_list = articles_data.get('articles', [])
            except requests.RequestException as e:
                print(f"An error occurred (fetch_everything_headlines): {e}")

        db_manager = DBManager()

        for article in articles_list:
            article_instance = Article(
                "newsapi.org",
                article.get('source', {}).get('id'),
                article.get('source', {}).get('name'),
                article.get('author'),
                article.get('title'),
                article.get('description'),
                article.get('url'),
                article.get('urlToImage'),
                article.get('publishedAt'),
                article.get('content'),
                article.get('rec_order'),
                article.get('added_timestamp'),
                article.get('scraped_timestamp'),
                article.get('scraped_website_content'),
                article.get('processed_timestamp')
            )

            if db_manager.is_article_processed(article_instance.url):
                continue

            db_manager.save_article(article_instance)
            return article_instance

        # No articles were found
        return None
