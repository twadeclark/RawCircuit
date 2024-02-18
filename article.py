class Article:
    def __init__(self, id, aggregator, source_id, source_name, author, title, description, url, url_to_image, published_at, content, rec_order, added_timestamp, scraped_timestamp, scraped_website_content, processed_timestamp):
        self.id = id
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
        self.rec_order = rec_order
        self.added_timestamp = added_timestamp
        self.scraped_timestamp = scraped_timestamp
        self.scraped_website_content = scraped_website_content
        self.processed_timestamp = processed_timestamp

        self.unstored_tags = []
        self.unstored_category = None
        self.model = None

        self.summary_prompt = None
        self.summary = None
        self.summary_dump = None
        self.shortened_content = None

        self.first_comment_prompt = None
        self.first_comment_prompt_keywords = None
        self.first_comment = None
        self.first_comment_flavors = None


    def __str__(self):
        return (self.id or "N/A") + "\n" + \
            (self.aggregator or "N/A") + "\n" + \
            (self.source_id or "N/A") + "\n" + \
            (self.source_name or "N/A") + "\n" + \
            (self.author or "N/A") + "\n" + \
            (self.title or "N/A") + "\n" + \
            (self.description or "N/A") + "\n" + \
            (self.url or "N/A") + "\n" + \
            (self.url_to_image or "N/A") + "\n" + \
            (self.published_at.strftime("%Y-%m-%d %H:%M:%S") if self.published_at else "N/A") + "\n" + \
            (self.content or "N/A") + "\n" + \
            (self.rec_order or "N/A") + "\n" + \
            (self.added_timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.added_timestamp else "N/A") + "\n" + \
            (self.scraped_timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.scraped_timestamp else "N/A") + "\n" + \
            (self.scraped_website_content or "N/A") + "\n" + \
            (self.processed_timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.processed_timestamp else "N/A") + "\n"
