from django import template
import markdown
import re

register = template.Library()

@register.filter
def markdown_to_html(text):
    return markdown.markdown(text)

@register.filter
def markdown_to_plain(text):
    html = markdown.markdown(text)
    plain_text = re.sub(r'<.*?>', '', html)
    plain_text_with_line_breaks = plain_text.replace('\n', '<br>')
    return plain_text_with_line_breaks