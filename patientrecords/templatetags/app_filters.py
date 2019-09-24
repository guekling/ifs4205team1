from django import template

register = template.Library()

@register.filter
def to_model_name(value):
  return value._meta.object_name