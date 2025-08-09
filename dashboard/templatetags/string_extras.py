from django import template

register = template.Library()

@register.filter(name='dash')
def dash(value: str) -> str:
    try:
        return str(value).replace('_', '-')
    except Exception:
        return ''
