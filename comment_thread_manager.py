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
            return None

    def get_article(self):
        return self.article

    def get_tags_comma_separated(self):
        return ", ".join(self.article.unstored_tags)
    
    def get_category(self):
        return self.article.unstored_category
