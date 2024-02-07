from datetime import datetime, timedelta
import configparser
import random
from newsapi import NewsApiClient
from aggregators.news_aggregator_base import NewsAggregator

class NewsApiOrgNews(NewsAggregator):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.news_search_term = config.get('general_configurations', 'news_search_term')
        self.from_date = datetime.now() - timedelta(days=config.getint('NewsAPI', 'days_back'))
        self.sort_by = config.get('NewsAPI', 'sortBy')
        self.api_key = config.get('NewsAPI', 'apiKey')
        self.newsapi = NewsApiClient(api_key=self.api_key)

    def get_name(self):
        return "NewsApiOrgNews"

    def fetch_articles(self):
        return random.choice(self.fetch_methods())(self.news_search_term)

    def fetch_methods(self):
        return [
            self.fetch_top_headlines,
            self.fetch_everything_headlines
        ]

    def fetch_top_headlines(self, query_term): # query_term does not seem to work for headlines
        top_headlines = self.newsapi.get_top_headlines( category='technology',
                                                        language='en')
        return top_headlines

    def fetch_everything_headlines(self, query_term):

        all_articles = self.newsapi.get_everything( q=query_term,
                                                    from_param=self.from_date,
                                                    sort_by='relevancy',
                                                    language='en')
        return all_articles
