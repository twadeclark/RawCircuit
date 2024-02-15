from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor
from article import Article


class DBManager:
    def __init__(self, config):
        self.config = config
        self.conn = self.connect_to_db()

    def connect_to_db(self):
        return psycopg2.connect(**self.config)

    def article_exists(self, url):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS(SELECT 1 FROM articles WHERE url = %s)
                """,
                (url,))
            row = cur.fetchone()
            if row is None:
                return False
            return row[0]

    def save_article(self, article_data):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO articles (aggregator, source_id, source_name, author, title, description, url, url_to_image, published_at, content, rec_order, added_timestamp, scraped_timestamp, processed_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (article_data.aggregator, article_data.source_id, article_data.source_name, article_data.author, article_data.title, article_data.description, article_data.url, article_data.url_to_image, article_data.published_at, article_data.content, article_data.rec_order, article_data.added_timestamp, article_data.scraped_timestamp, article_data.processed_timestamp))
            self.conn.commit()

    def get_random_article(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, aggregator, source_id, source_name, author, title, description, url, url_to_image, published_at, content, rec_order, added_timestamp, scraped_timestamp, scraped_website_content, processed_timestamp
                FROM articles
                ORDER BY RANDOM() --published_at DESC
                LIMIT 1
                """)
            row = cur.fetchone()
            if row is None:
                return None
            return Article(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],row[10],row[11],row[12],row[13],row[14],row[15])

    def get_next_article_to_scrape(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT a.id, a.aggregator, a.source_id, a.source_name, a.author, a.title, a.description, a.url, a.url_to_image, a.published_at, a.content, a.rec_order, a.added_timestamp, a.scraped_timestamp, a.scraped_website_content, a.processed_timestamp
                FROM articles a
                WHERE scraped_timestamp IS NULL AND processed_timestamp IS NULL AND scraped_website_content IS NULL
                ORDER BY added_timestamp, rec_order
                """)
            row = cur.fetchone()
            if row is None:
                return None
            return Article(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],row[10],row[11],row[12],row[13],row[14],row[15])

    def get_next_article_to_process(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT a.id, a.aggregator, a.source_id, a.source_name, a.author, a.title, a.description, a.url, a.url_to_image, a.published_at, a.content, a.rec_order, a.added_timestamp, a.scraped_timestamp, a.scraped_website_content, a.processed_timestamp
                FROM articles a
                WHERE processed_timestamp IS NULL
                ORDER BY added_timestamp, rec_order
                """)
            row = cur.fetchone()
            if row is None:
                return None
            return Article(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],row[10],row[11],row[12],row[13],row[14],row[15])

    def update_scrape_time(self, article):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE articles
                SET scraped_timestamp = NOW()
                WHERE id = %s
                """,
                (article.id,))
            self.conn.commit()

    def update_process_time(self, article):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE articles
                SET processed_timestamp = NOW()
                WHERE id = %s
                """,
                (article.id,))
            self.conn.commit()

    def update_scraped_website_content(self, article):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE articles
                SET scraped_website_content = %s
                WHERE id = %s
                """,
                (article.scraped_website_content, article.id))
            self.conn.commit()


    def get_models_with_none_success(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT model_name
                FROM model_records
                WHERE success IS NULL
                """)
            rows = cur.fetchall()
            if rows is None:
                return None
            return rows

    def insert_model_record(self, model_name):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO model_records (model_name, attempt_time)
                VALUES (%s, %s)
                """,
                (model_name, datetime.now()))
            self.conn.commit()
            return cur.lastrowid

    def update_model_record(self, model_name, success, disposition):
        with self.conn.cursor() as cur:
            success_bit = '1' if success else '0'
            cur.execute("""
                UPDATE model_records
                SET attempt_time = %s, success = %s::bit(1), disposition = %s
                WHERE model_name = %s
                """,
                (datetime.now(), success_bit, disposition, model_name))
            self.conn.commit()

    def get_model_name_list_by_list_of_model_names(self, list_of_model_names):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT model_name
                FROM model_records
                WHERE model_name = ANY(%s)
                """,
                (list_of_model_names,))
            rows = cur.fetchall()
            if rows is None:
                return None
            return rows
