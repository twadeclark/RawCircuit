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

        #     "source": {
        #         "id": "engadget",
        #         "name": "Engadget"
        #     },
        #     "author": "Devindra Hardawar",
        #     "title": "Roku's 'high-end' Pro Series TVs feature Mini LED screens",
        #     "description": "Roku is stepping into premium TV territory at CES 2024 with its new Pro Series sets, which feature Mini LED backlighting for better brightness and contrast, as well as enhanced audio. The company announced its first self-made TVs at CES last year — a surprisi…",
        #     "url": "https://www.engadget.com/roku-high-end-pro-series-tvs-feature-mini-led-screens-164354589.html",
        #     "urlToImage": "https://s.yimg.com/os/creatr-uploaded-images/2024-01/a792c560-aa55-11ee-a5ed-c26c2d6b7edd",
        #     "publishedAt": "2024-01-03T16:43:54Z",
        #     "content": "Roku is stepping into premium TV territory at CES 2024 with its new Pro Series sets, which feature Mini LED backlighting for better brightness and contrast, as well as enhanced audio. The company ann… [+2510 chars]"
        # },

        