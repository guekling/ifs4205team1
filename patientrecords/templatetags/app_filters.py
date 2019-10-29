from django.conf import settings

from django import template
from core.models import User, Patient, Healthcare, Researcher, Admin

import os

register = template.Library()

@register.simple_tag
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

@register.filter
def get_patient_full_name(patient):
  return patient.username.get_full_name()

@register.filter
def get_log_status(value):
  if (value == 1):
    return "OK"
  elif (value == 0):
    return "ERROR"
  else:
    return ""

@register.filter
def get_log_user(id):
  user = User.objects.filter(uid=id)

  if user.exists:
    return user.first()

  patient = Patient.objects.filter(id=id)

  if patient.exists:
    return patient.first()

  healthcare = Healthcare.objects.filter(id=id)

  if healthcare.exists:
    return healthcare.first()

  researcher = Researcher.objects.filter(id=id)

  if researcher.exists:
    return researcher.first()
  
  admin = Admin.objects.filter(id=id)

  if admin.exists:
    return admin.first()
  
  return None

@register.filter
def get_record_path(id):
  return os.path.join(settings.PROTECTED_MEDIA_PATH, str(id))