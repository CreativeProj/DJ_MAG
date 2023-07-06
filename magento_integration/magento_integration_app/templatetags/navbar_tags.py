from django import template

register = template.Library()

@register.inclusion_tag('includes/navbar.html')
def navbar():
    return {}

@register.inclusion_tag('includes/head.html')
def head():
    return {}