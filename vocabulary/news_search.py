import random
import yaml


class SearchTerms():
    def __init__(self):
        with open('news_search_terms.yaml', 'r', encoding='utf-8') as file:
            self.news_search_terms = yaml.safe_load(file)

    def get_random_term(self):
        key_list = list(self.news_search_terms.keys())
        random_category = random.choice(key_list)
        random_term = random.choice(self.news_search_terms[random_category])
        return random_category, random_term

    def find_tags_in_article(self, article):
        article_text = article.content.lower() + article.title.lower() + article.description.lower()
        tags = []
        for category in self.news_search_terms:
            for word in self.news_search_terms[category]:
                if word in article_text:
                    tags.append(word)
        return tags
