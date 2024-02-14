import random
import yaml


class SearchTerms():
    def __init__(self):
        with open('vocabulary/categories_tags_keywords.yaml', 'r', encoding='utf-8') as file:
            self.categories_tags_keywords = yaml.safe_load(file)

    def get_random_term(self):
        key_list = list(self.categories_tags_keywords.keys())
        random_category = random.choice(key_list)
        random_term = random.choice(self.categories_tags_keywords[random_category])
        return random_category, random_term

    def categorize_article_add_tags(self, article_to_process):
        article_text = article_to_process.scraped_website_content.lower()

        best_fit_category = None
        best_fit_score = 0
        all_assigned_tags = []

        for category, tags in self.categories_tags_keywords.items():
            current_category_score = 0

            for tag, keywords in tags.items():
                for keyword in keywords:
                    if keyword.lower() in article_text:
                        current_category_score += 1
                        all_assigned_tags.append(tag)
                        break

            if current_category_score > best_fit_score:
                best_fit_score = current_category_score
                best_fit_category = category

        article_to_process.unstored_category = best_fit_category
        article_to_process.unstored_tags = all_assigned_tags
