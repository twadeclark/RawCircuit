# article_fetcher.py
import configparser
import psycopg2

from article import Article

config = configparser.ConfigParser()
config.read('config.ini')

# Get the database connection parameters
db_config = config['postgresql']
host = db_config.get('host')
database = db_config.get('database')
user = db_config.get('user')
password = db_config.get('password')

# Connect to the database
conn = psycopg2.connect(host=host, database=database, user=user, password=password)


def fetch_article():
    # For now, we are returning a dummy Article object.
    # In a real scenario, these values would come from an actual news aggregator.
    dummy_aggregator = "Dummy News Aggregator"
    dummy_url = "http://example.com/dummy-article"
    dummy_content = "This is the dummy content of the article."

    return Article(dummy_aggregator, dummy_url, dummy_content)
