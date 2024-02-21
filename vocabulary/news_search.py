import random
import re
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
        # self._category_and_tags_by_content(article_to_process)
        self._category_and_tags_by_model(article_to_process)

        print("category :", article_to_process.unstored_category)
        print("tags     :", article_to_process.unstored_tags)

    def _category_and_tags_by_model(self, article_to_process):
        model_name = article_to_process.model["name"]
        all_assigned_tags = []
        best_fit_category = ""

        if 'chat' in model_name.lower():
            all_assigned_tags.append("chat")

        if 'instruct' in model_name.lower():
            all_assigned_tags.append("instruct")

        if 'gguf' in model_name.lower():
            all_assigned_tags.append("gguf")

        if 'code' in model_name.lower():
            all_assigned_tags.append("code")

        if 'uncensored' in model_name.lower():
            all_assigned_tags.append("uncensored")

        if 'tiny' in model_name.lower():
            all_assigned_tags.append("tiny")

        # token_count = just the numbers from a regex does this: match a non-number character, followed one or more number characters, followed by a b or B, followed by an underscore or non-letter character or end of string
        token_count = re.findall(r'(?<!\d)\d+[bB](?![a-zA-Z])', model_name)
        if token_count:
            all_assigned_tags.append(f"{token_count[0].lower()}")


        if 'gpt' in model_name.lower():
            best_fit_category = "gpt"

        if 'falcon' in model_name.lower():
            best_fit_category = "falcon"
            
        if 'phi' in model_name.lower():
            best_fit_category = "phi"

        if 'llama' in model_name.lower():
            best_fit_category = "llama"

        if 'mistral' in model_name.lower():
            best_fit_category = "mistral"

        if 'mixtral' in model_name.lower():
            best_fit_category = "mixtral"

        article_to_process.unstored_category = best_fit_category
        article_to_process.unstored_tags = all_assigned_tags


    def _category_and_tags_by_content(self, article_to_process):
        article_text = article_to_process.shortened_content.lower()

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
