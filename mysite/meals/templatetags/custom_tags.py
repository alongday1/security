from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):  # 确保传入的是字典
        return dictionary.get(key)
    return None  # 如果不是字典，返回 None
