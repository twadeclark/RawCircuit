import random
import yaml


class SearchTerms():
    def __init__(self):
        with open('categories_tags_keywords.yaml', 'r', encoding='utf-8') as file:
            self.categories_tags_keywords = yaml.safe_load(file)

    def get_random_term(self):
        key_list = list(self.categories_tags_keywords.keys())
        random_category = random.choice(key_list)
        random_term = random.choice(self.categories_tags_keywords[random_category])
        return random_category, random_term

    # def find_tags_in_article(self, article):
    #     article_text = article.content.lower() + article.title.lower() + article.description.lower()
    #     tags = []
    #     for category in self.categories_tags_keywords:
    #         for word in self.categories_tags_keywords[category]:
    #             if word in article_text:
    #                 tags.append([word, article_text.count(word)])
    #     return tags






    # import yaml

    # Function to categorize a news article and assign tags
    def categorize_article(self, article_text):
        # Convert article text to lower case for matching
        article_text = article_text.lower()

        # Initialize variables to store the best fit category and its tags
        best_fit_category = None
        best_fit_score = 0
        assigned_tags = []

        # Iterate over each category and its tags
        for category, tags in self.categories_tags_keywords.items():
            current_category_score = 0
            current_category_tags = []

            # Check each tag in the category
            for tag, keywords in tags.items():
                for keyword in keywords:
                    # Check if keyword is in article
                    if keyword.lower() in article_text:
                        current_category_score += 1
                        current_category_tags.append(tag)
                        break  # Move to the next tag after a keyword match

            # Determine if this category is the best fit so far
            if current_category_score > best_fit_score:
                best_fit_score = current_category_score
                best_fit_category = category
                assigned_tags = current_category_tags

        return best_fit_category, assigned_tags





    # Revised function to categorize a news article and assign tags, keeping all matched tags across categories
    def categorize_article_all_tags(self, article_text):
        # Convert article text to lower case for matching
        article_text = article_text.lower()

        # Initialize variables to store the best fit category and all tags
        best_fit_category = None
        best_fit_score = 0
        all_assigned_tags = []

        # Iterate over each category and its tags
        for category, tags in self.categories_tags_keywords.items():
            current_category_score = 0

            # Check each tag in the category
            for tag, keywords in tags.items():
                for keyword in keywords:
                    # Check if keyword is in article
                    if keyword.lower() in article_text:
                        current_category_score += 1
                        all_assigned_tags.append(tag)
                        break  # Move to the next tag after a keyword match

            # Determine if this category is the best fit so far
            if current_category_score > best_fit_score:
                best_fit_score = current_category_score
                best_fit_category = category

        return best_fit_category, all_assigned_tags

    # Categorize the sample article while keeping all matched tags
    # category, tags = categorize_article_all_tags(sample_article, categories_tags_keywords)
    # category, tags



