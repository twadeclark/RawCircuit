class CommentThreadManager:
    def __init__(self, article):
        self.comments = []
        self.article = article

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
