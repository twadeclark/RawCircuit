import configparser
import psycopg2

class DBManager:
    def __init__(self):
        self.config = self.read_db_config()
        self.conn = self.connect_to_db()

    def read_db_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config['postgresql']

    def connect_to_db(self):
        return psycopg2.connect(**self.config)

    def is_article_processed(self, url):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM articles WHERE url = %s", (url,))
            return cur.fetchone() is not None

    def save_article(self, article_data):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO articles (aggregator, source_id, source_name, author, title, description, url, url_to_image, published_at, content)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (article_data.aggregator, article_data.source_id, article_data.source_name, article_data.author, article_data.title, article_data.description, article_data.url, article_data.url_to_image, article_data.published_at, article_data.content))
            self.conn.commit()
