from django import template
import math

register = template.Library()

@register.simple_tag
def star_rating(rating, max_stars=5):

    full_stars = int(math.floor(rating))
    half_star = (rating - full_stars) >= 0.5
    empty_stars = max_stars - full_stars - (1 if half_star else 0)

    stars_html = ''
    stars_html += '★' * full_stars
    if half_star:
        stars_html += '★'
    stars_html += '☆' * empty_stars

    return stars_html
