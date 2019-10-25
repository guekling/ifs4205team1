from django.conf import settings
from django.shortcuts import render

def home(request):
  context = {}

  return render(request, 'home.html', context)

def protected_media(request):
  response['Content-Type'] = ''
  response['X-Accel-Redirect'] = '/media/' + request.path
  return response