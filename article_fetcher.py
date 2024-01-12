# # article_fetcher.py
# import configparser
# import psycopg2
# from article import Article

# def fetch_article_null():
#     config = configparser.ConfigParser()
#     config.read('config.ini')

#     # Get the database connection parameters
#     db_config = config['postgresql']
#     host = db_config.get('host')
#     database = db_config.get('database')
#     user = db_config.get('user')
#     password = db_config.get('password')

#     # Connect to the database
#     conn = psycopg2.connect(host=host, database=database, user=user, password=password)
#     cur = conn.cursor()

#     try:
#         # SQL query to select a random row
#         cur.execute("SELECT name, url FROM news_aggregators ORDER BY RANDOM() LIMIT 1")

#         # Fetch one record
#         row = cur.fetchone()
#         if row:
#             aggregator_name, aggregator_url = row
#             # Dummy content for now
#             dummy_content = "This is the dummy content of the article."
#         else:
#             # Fallback values if the table is empty
#             aggregator_name = ""
#             aggregator_url = ""
#             dummy_content = ""

#         # Return an Article object
#         return Article(aggregator_name, aggregator_url, dummy_content)

#     finally:
#         # Close the database connection
#         cur.close()
#         conn.close()
