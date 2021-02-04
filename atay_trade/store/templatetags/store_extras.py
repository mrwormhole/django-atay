from django import template
register = template.Library()

@register.filter(name="indexOf")
def indexOf(indexable, i):
    return indexable[i]