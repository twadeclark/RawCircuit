import random
import json
import re


# prompt engineering: https://cookbook.openai.com/articles/techniques_to_improve_reliability

class InstructionGenerator:
    def __init__(self, prompt_tier):
        self.prompt_tier = prompt_tier
        with open('prompt_templates.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        with open('values.json', 'r', encoding='utf-8') as file:
            self.values = json.load(file)
        self.add_user_babble = False

    def handle_conversation_roles_must_alternate(self):
        self.add_user_babble = True

    def _get_random_value(self, category):
        return random.choice(self.values[category])

    def generate_summary_prompt_instruct(self, article_text):
        categories = self.values.keys()
        selected_values = {category: self._get_random_value(category) for category in categories}
        inst_tmp = self.config[self.prompt_tier]['summary_prompt_instruct']
        placeholders = set(re.findall(r'\{(\w+)\}', inst_tmp))
        filtered_selected_values = {k: v for k, v in selected_values.items() if k in placeholders}
        system_content = inst_tmp.format(article_text=article_text, **filtered_selected_values)
        prompt_keywords = ', '.join(filtered_selected_values.values())

        return system_content, prompt_keywords

    def generate_summary_prompt_instruct_chat(self, article_text):
        categories = self.values.keys()
        selected_values = {category: self._get_random_value(category) for category in categories}
        inst_tmp = self.config[self.prompt_tier]['summary_prompt_instruct_chat']
        placeholders = set(re.findall(r'\{(\w+)\}', inst_tmp))
        filtered_selected_values = {k: v for k, v in selected_values.items() if k in placeholders}
        system_content = inst_tmp.format(article_text=article_text, **filtered_selected_values)
        prompt_keywords = ', '.join(filtered_selected_values.values())

        formatted_messages = []
        formatted_messages.append({"role": "user", "content": system_content})
        return formatted_messages, prompt_keywords

    def generate_summary_prompt_chat(self, article_text):
        categories = self.values.keys()
        selected_values = {category: self._get_random_value(category) for category in categories}
        inst_tmp = self.config[self.prompt_tier]['summary_prompt_chat']
        placeholders = set(re.findall(r'\{(\w+)\}', inst_tmp))
        filtered_selected_values = {k: v for k, v in selected_values.items() if k in placeholders}
        system_content = inst_tmp.format(**filtered_selected_values)
        prompt_keywords = ', '.join(filtered_selected_values.values())

        if self.add_user_babble:
            formatted_messages = [  {"role": "user", "content": "You are a helpful assistant."},
                                    {"role": "assistant", "content": article_text},
                                    {"role": "user", "content": system_content}]
        else:
            formatted_messages = [  {"role": "system", "content": system_content},
                                    {"role": "user", "content": article_text}]

        return formatted_messages, prompt_keywords

    def generate_first_comment_prompt(self, summary_text):
        categories = self.values.keys()
        selected_values = {category: self._get_random_value(category) for category in categories}
        inst_tmp = self.config[self.prompt_tier]['first_comment_prompt']
        placeholders = set(re.findall(r'\{(\w+)\}', inst_tmp))
        filtered_selected_values = {k: v for k, v in selected_values.items() if k in placeholders}
        system_content = inst_tmp.format(**filtered_selected_values)
        prompt_keywords = ', '.join(filtered_selected_values.values())

        if self.add_user_babble:
            formatted_messages = [  {"role": "user", "content": "You are a helpful assistant."},
                                    {"role": "assistant", "content": summary_text},
                                    {"role": "user", "content": system_content}]
        else:
            formatted_messages = [  {"role": "system", "content": system_content},
                                    {"role": "user", "content": summary_text}]

        return formatted_messages, prompt_keywords

    def generate_loop_prompt(self, summary, parent_comment):
        categories = self.values.keys()
        selected_values = {category: self._get_random_value(category) for category in categories}
        inst_tmp = self.config[self.prompt_tier]['loop_comment_prompt']
        placeholders = set(re.findall(r'\{(\w+)\}', inst_tmp))
        filtered_selected_values = {k: v for k, v in selected_values.items() if k in placeholders}
        system_content = inst_tmp.format(summary=summary, **filtered_selected_values)
        prompt_keywords = ', '.join(filtered_selected_values.values())

        if self.add_user_babble:
            formatted_messages = [  {"role": "user", "content": "You are a helpful assistant."},
                                    {"role": "assistant", "content": parent_comment},
                                    {"role": "user", "content": system_content}]
        else:
            formatted_messages = [  {"role": "system", "content": system_content},
                                    {"role": "user", "content": parent_comment}]

        return formatted_messages, prompt_keywords
