from django import template
import re

register = template.Library()

@register.filter
def youtube_id(url):
    pattern = r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else ''
