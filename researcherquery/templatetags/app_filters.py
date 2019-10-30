from django.conf import settings
from django import template

import os

register = template.Library()

@register.filter
def get_image_path(id):
  return os.path.join(settings.RESEARCHER_IMAGE_PATH, str(id))

@register.filter
def get_video_path(id):
  return os.path.join(settings.RESEARCHER_VIDEO_PATH, str(id))