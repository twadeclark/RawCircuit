import configparser
import psycopg2
from article import Article

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

    def save_article(self, article_data):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO articles (aggregator, source_id, source_name, author, title, description, url, url_to_image, published_at, content, rec_order, added_timestamp, scraped_timestamp, processed_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (article_data.aggregator, article_data.source_id, article_data.source_name, article_data.author, article_data.title, article_data.description, article_data.url, article_data.url_to_image, article_data.published_at, article_data.content, article_data.rec_order, article_data.added_timestamp, article_data.scraped_timestamp, article_data.processed_timestamp))
            self.conn.commit()

    def get_random_article(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT aggregator, source_id, source_name, author, title, description, url, url_to_image, published_at, content, rec_order, added_timestamp, scraped_timestamp, scraped_website_content, processed_timestamp
                FROM articles
                ORDER BY RANDOM() --published_at DESC
                LIMIT 1
                """)
            row = cur.fetchone()
            if row is None:
                return None
            return Article(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],row[10],row[11],row[12],row[13],row[14])

    def get_next_article_to_process(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT a.aggregator, a.source_id, a.source_name, a.author, a.title, a.description, a.url, a.url_to_image, a.published_at, a.content, a.rec_order, a.added_timestamp, a.scraped_timestamp, a.scraped_website_content, a.processed_timestamp
                FROM articles a
                INNER JOIN (
                    SELECT added_timestamp, MIN(rec_order) as min_rec_order
                    FROM articles
                    WHERE scraped_timestamp IS NULL AND processed_timestamp IS NULL
                    GROUP BY added_timestamp
                    ORDER BY added_timestamp DESC
                    LIMIT 1
                ) as latest_group ON a.added_timestamp = latest_group.added_timestamp AND a.rec_order = latest_group.min_rec_order
                """)
            row = cur.fetchone()
            if row is None:
                return None
            return Article(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],row[10],row[11],row[12],row[13],row[14])

    def update_scrape_time(self, article):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE articles
                SET scraped_timestamp = NOW()
                WHERE url = %s
                """,
                (article.url,))
            self.conn.commit()

    def update_process_time(self, article):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE articles
                SET processed_timestamp = NOW()
                WHERE url = %s
                """,
                (article.url,))
            self.conn.commit()

    def update_scraped_website_content(self, article):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE articles
                SET scraped_website_content = %s
                WHERE url = %s
                """,
                (article.scraped_website_content, article.url))
            self.conn.commit()

            


