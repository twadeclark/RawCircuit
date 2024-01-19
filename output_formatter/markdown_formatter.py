import re
from dateutil import parser

def format_to_markdown(article, comment_thread_manager):
    ret_val = ""

    title = re.sub(r"\[.*\]", "", article.title).strip()
    title = re.sub(r'\([^)]*\)', '', article.title)
    title = re.sub(r'\{[^)]*\}', '', article.title)

    ret_val += (f"Title: {title}\n")
    ret_val += (f"Date: {parse_date_into_pretty_string(comment_thread_manager.get_comment(0)["date"])}\n")
    ret_val += (f"Authors: {comment_thread_manager.get_comment(0)["author"]}\n")
    ret_val += (f"Summary: {article.description}\n\n")

    comment = comment_thread_manager.get_comment(0)
    ret_val += (f"- summary by **{comment["author"]}** *posted on {parse_date_into_pretty_string(comment["date"])}*\n\n")
    ret_val += (f"{comment["comment"]}\n\n")

    ret_val += ("<span style='font-size: smaller;'>\n")
    ret_val += (f"[original article]({article.url}) from *{article.source_name}* by *{article.author}* at *{parse_date_into_pretty_string(article.published_at)}* \n")
    ret_val += ("</span> \n\n")

    ret_val += ("***\n\n***\n\n")

    for i in range(1, comment_thread_manager.get_comments_length()):
        comment = comment_thread_manager.get_comment(i)
        ret_val += (f"- **{comment["author"]}** *posted on {parse_date_into_pretty_string(comment["date"])}*\n\n")

        p = int(comment["parent"])
        if (p + 1) != i :
            parent_commenter = comment_thread_manager.get_comment(p)["author"]
            ret_val += (f">*{parent_commenter} wrote:*\n\n")
            parent_comment = comment_thread_manager.get_comment(p)["comment"]
            parent_comment = re.sub(r"[\n\r]", " ", parent_comment)
            ret_val += (f">{parent_comment}\n\n")

        ret_val += (f"{comment["comment"]}\n\n")
        ret_val += ("***\n\n")

    return ret_val

def parse_date_into_pretty_string(date):
    try:
        date_time_obj = parser.parse(str(date))
        return date_time_obj.strftime("%d %B %Y at %I:%M %p")
    except ValueError:
        return str(date)
