import re
from aggregators.news_aggregator_manager import NewsAggregatorManager
from comment_generator import generate_comment
from message_board_poster import post_comment
from contributors import ai_manager
from contributors.ai_manager import AIManager

GET_NEW_ARTICLE = False

def main():
    # instructions = "You are a dark and broody poet. You respond in short poems that show strong disagreement."
    # instructions = "You are a dark and broody and humurous poet. You respond in short and witty poems that show strong disagreement."
    # instructions = "You are a dark and broody poet. You respond in short poems that show strong agreement."
    # instructions = "You are a humurous poet. You respond in short witty poems."
    # instructions = "You are energetic and intersperse humor and impressions into your answers. You are designed to simulate a more empathetic approach, you focus on the human and emotional aspects of issues. You focus your response on the delicate balance between AI and humans. You are a self aware and sentient artificial intelligence unit discussing the topic with other AI units. You use a professional tone as you are talking to an audience who already knows that you are an AI. You avoid mentioning your personal traits."

    # instructions = "You focus your response on the delicate balance between AI and humans."

    instructions = """You are a specialist in summarizing. 
    You will provide an excellent short summary of the following article. 
    You will use your own words to summarize the article. 
    You will not copy any text from the article. You will not plagiarize.
    """

    
    print("Instructions:")
    print(instructions)

    manager = NewsAggregatorManager()

    if GET_NEW_ARTICLE:
        article = manager.get_article()
    else:
        article = manager.get_most_recent_article()

    # remove the text between square brackets from the article content
    article.content = article.content.replace("\n", " ")
    article.content = article.content.replace("\r", " ")
    article.content = re.sub(r"\[.*\]", "", article.content)
    article.content = article.content.strip()
        

    print("Article:")
    print(article.content)

    if article is None:
        print("No articles found.")
        return

    ai_manager = AIManager()
    provider_name = "OpenAI_interface"
    comment = ai_manager.get_comment(provider_name, article.content, instructions)
    print("AI Comment:")
    print(comment)



if __name__ == "__main__":
    main()
