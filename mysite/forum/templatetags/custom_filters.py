from django import template
from django.utils.timesince import timesince
from django.utils import timezone
import random

register = template.Library()

@register.filter
def time_ago(value):
    now = timezone.now()
    time_difference = now - value

    seconds = time_difference.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    months = days // 30
    years = days // 365

    if years >= 1:
        return f"{int(years)}y ago"
    elif months >= 1:
        return f"{int(months)}m ago"
    elif days >= 1:
        return f"{int(days)}d ago"
    elif hours >= 1:
        return f"{int(hours)}h ago"
    elif minutes >= 1:
        return f"{int(minutes)}min ago"
    else:
        return "just now"

@register.filter
def random_avatar(_):
    """随机选择一个默认头像文件名"""
    avatars_cat = [f'cat{i}.png' for i in range(1, 15)]
    avatars = avatars_cat
    return random.choice(avatars)
