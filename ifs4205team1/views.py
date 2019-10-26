from django.contrib.auth.decorators import login_required

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect

from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos
from userlogs.models import Logs

from itertools import chain

def home(request):
  context = {}

  return render(request, 'home.html', context)

@login_required(login_url='/')
def protected_record(request, record_id):
  """
  Show information of a single medical record.
  """
  try:
    record = get_record(record_id)
    record = record[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Record ID is invalid.')
    return redirect('home')

  model = get_model(record)

  # Checks if user has permission to view this record
  if (model == 'Documents'):
    if ((not record.has_permission(request.user)) or (record.owner_id != request.user)):
      Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Permission Denied.')
      return redirect('home')
  else:
    if ((not record.has_permission(request.user.healthcare_username)) and (record.owner_id != request.user)):
      Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Permission Denied.')
      return redirect('home')
  
  Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_OK, details='View Protected Record.')

  context = {
    'record': record,
  }

  return render(request, 'protected_record.html', context)

def protected_media(request):
  response = HttpResponse()
  response['Content-Type'] = ''
  response['X-Accel-Redirect'] = '/media/images/MRI_Image_2.jpg'
  return response

##########################################
############ Helper Functions ############
##########################################

STATUS_OK = 1
STATUS_ERROR = 0

def get_record(record_id):
  readings = Readings.objects.filter(id=record_id)
  timeseries = TimeSeries.objects.filter(id=record_id)
  documents = Documents.objects.filter(id=record_id)
  images = Images.objects.filter(id=record_id)
  videos = Videos.objects.filter(id=record_id)

  return list(chain(readings, timeseries, documents, images, videos))

def get_model(record):
  return record._meta.object_name