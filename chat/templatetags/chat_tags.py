from django import template
from django.utils.timesince import timesince
from django.utils.timezone import now

register = template.Library()

@register.filter
def last_seen_display(value):
    if not value:
        return "давно"
    delta = now() - value
    if delta.total_seconds() < 60:
        return "щойно"
    return f"{timesince(value)} тому"
