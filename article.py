# article.py

class Article:
    def __init__(self, aggregator, source_id, source_name, author, title, description, url, url_to_image, published_at, content):
        self.aggregator = aggregator
        self.source_id = source_id
        self.source_name = source_name
        self.author = author
        self.title = title
        self.description = description
        self.url = url
        self.url_to_image = url_to_image
        self.published_at = published_at
        self.content = content

    def __str__(self):
        return (self.aggregator or "N/A") + "\n" + \
            (self.source_id or "N/A") + "\n" + \
            (self.source_name or "N/A") + "\n" + \
            (self.author or "N/A") + "\n" + \
            (self.title or "N/A") + "\n" + \
            (self.description or "N/A") + "\n" + \
            (self.url or "N/A") + "\n" + \
            (self.url_to_image or "N/A") + "\n" + \
            (self.published_at.strftime("%Y-%m-%d %H:%M:%S") if self.published_at else "N/A") + "\n" + \
            (self.content or "N/A") + "\n"
