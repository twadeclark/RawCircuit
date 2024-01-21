class CommentThreadManager:
    def __init__(self, article, category, tags):
        self.comments = []
        self.article = article
        self.category = category
        self.tags = tags

    def add_comment(self, parent, comment, author, date):
        self.comments.append({
            "parent": parent,
            "comment": comment,
            "author": author,
            "date": date
        })

    def get_comments_length(self):
        return len(self.comments)

    def get_comment(self, index):
        if 0 <= index < len(self.comments):
            return self.comments[index]
        else:
            return None  # or raise an exception, based on how you want to handle it

    def get_article(self):
        return self.article

    def get_tags_comma_separated(self):
        return ", ".join(self.tags)
    
    def get_category(self):
        return self.category
