from django import template

register = template.Library()

@register.filter
def to_model_name(value):
  return value._meta.object_name

@register.filter
def get_date(timestamp):
  return timestamp.strftime("%a, %d %b %Y")

@register.filter
def get_time(timestamp):
  return timestamp.strftime("%I:%M %p")

@register.filter
def get_datetime(timestamp):
  return timestamp.strftime("%a, %d %b %Y %I:%M %p")

@register.filter
def get_perm(value):
  if (value == 1):
    return "No Access"
  elif (value == 2):
    return "Read Only Access"
  elif (value == 3):
    return "Read & Set Permission Access"
  elif (value == 4):
    return "Owner"
  else:
    return ""

@register.filter
def get_full_name(user):
  return user.get_full_name()