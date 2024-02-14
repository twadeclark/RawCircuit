import datetime
class CommentThreadManager:
    def __init__(self):
        self.comments = []
        self.article = None
        self.start_time = datetime.datetime.now()

    def add_comment(self, parent, comment, author, prompt_keywords, date):
        self.comments.append({
            "parent": parent,
            "comment": comment,
            "author": author,
            "prompt_keywords": prompt_keywords,
            "date": date
        })

    def get_duration(self):
        return datetime.datetime.now() - self.start_time

    def get_start_time(self):
        return self.start_time

    def set_article(self, article):
        self.article = article

    def get_comments_length(self):
        return len(self.comments)

    def get_comment(self, index):
        if 0 <= index < len(self.comments):
            return self.comments[index]
        else:
            return None

    def get_article(self):
        return self.article

    def get_tags_comma_separated(self):
        return ", ".join(self.article.unstored_tags)

    def get_category(self):
        return self.article.unstored_category
