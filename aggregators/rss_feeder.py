import feedparser

class RSSFeeder:
    def __init__(self):
        pass

    def get_name(self):
        return "RSSFeeder"
    
    def fetch_articles(self, url):
        feed = feedparser.parse(url)
        entries = feed.entries
        for entry in entries:
            entry.url = entry.link
            entry.title = entry.title
            entry.published = entry.published
            entry.rec_order = 0



        return feed.entries





# # URL of the RSS feed
# rss_url = 'http://example.com/rss'

# # Parse the RSS feed
# feed = feedparser.parse(rss_url)

# # Loop through the entries and print the title and link
# for entry in feed.entries:
#     print(entry.title)
#     print(entry.link)
