from django.contrib.auth.decorators import login_required, user_passes_test

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect

from core.models import User
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos
from researcherquery.models import SafeImages, SafeVideos
from userlogs.models import Logs

import os
from itertools import chain
from mimetypes import guess_type

def home(request):
  context = {}

  return render(request, 'home.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/')
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
  if (User.is_healthcare(request.user)):
    if (model == 'Documents'): 
      # Checks if healthcare has permission to view doc OR if user is owner of healthcare prof note
      if ((not record.has_permission(request.user)) or (not record.is_owner_healthcare_note(request.user))):
        Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Permission Denied.')
        return redirect('home')
    else:
      # Checks if healthcare has permission to view record
      if (not record.has_permission(request.user.healthcare_username)):
        Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Permission Denied.')
        return redirect('home')
  elif (User.is_patient(request.user)):
    # Checks if record belongs to the patient
    if (not record.is_patient(request.user.patient_username)):
      Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Permission Denied.') 
      return redirect('home')

  Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_OK, details='View Protected Record ' + str(record_id))

  context = {
    'record': record,
  }

  return render(request, 'protected_record.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/')
def download_protected_record(request, record_id):
  """
  Download a single medical record
  """
  try:
    record = get_record(record_id)
    record = record[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Download Protected Record] Record ID is invalid.')
    return redirect('home')

  model = get_model(record)

  # Checks if user has permission to download this record
  if (User.is_healthcare(request.user)):
    if (model == 'Documents'): 
      # Checks if healthcare has permission to view doc OR if user is owner of healthcare prof note
      if ((not record.has_permission(request.user)) or (not record.is_owner_healthcare_note(request.user))):
        Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Permission Denied.')
        return redirect('home')
    else:
      # Checks if healthcare has permission to view record
      if (not record.has_permission(request.user.healthcare_username)):
        Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Permission Denied.')
        return redirect('home')
  elif (User.is_patient(request.user)):
    # Checks if record belongs to the patient
    if (not record.is_patient(request.user.patient_username)):
      Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Permission Denied.')
      return redirect('home')

  Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_OK, details='View Protected Record ' + str(record_id)) 
  file_path = record.data.path
  file_name = record.data.name.split('/', 1)[1]

  with open(file_path, 'rb') as record:
    content_type = guess_type(file_path)[0]
    response = HttpResponse(record, content_type=content_type)
    response['Content-Length'] = os.path.getsize(file_path)
    response['Content-Disposition'] = "attachment; filename=%s" %  file_name

    Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_OK, details='Download Protected Record ' + str(record_id))

    return response  

@login_required(login_url='/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/')
def protected_media(request, record_id):
  """
  Serves a single medical record file.
  """
  try:
    record = get_record(record_id)
    record = record[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[View Protected Media] Record ID is invalid.')
    return redirect('home')

  model = get_model(record)

  # Checks if user has permission to view this record
  if (User.is_healthcare(request.user)):
    if (model == 'Documents'): 
      # Checks if healthcare has permission to view doc OR if user is owner of healthcare prof note
      if ((not record.has_permission(request.user)) and (not record.is_owner_healthcare_note(request.user))):
        Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Permission Denied.')
        return redirect('home')
    else:
      # Checks if healthcare has permission to view record
      if (not record.has_permission(request.user.healthcare_username)):
        Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Permission Denied.')
        return redirect('home')
  elif (User.is_patient(request.user)):
    # Checks if record belongs to the patient
    if (not record.is_patient(request.user.patient_username)):
      Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_ERROR, details='[Protected Record] Permission Denied.')
      return redirect('home') 

  Logs.objects.create(type='READ', user_id=request.user.uid, interface='USER', status=STATUS_OK, details='View Protected Record ' + str(record_id))

  data_path = record.data.name

  response = HttpResponse()
  response['Content-Type'] = ''
  response['X-Accel-Redirect'] = '/media/%s' % data_path
  return response

def researcher_image(request, record_id):
  """
  Serves a single anonymised medical record file.
  """
  print("RESEARCHER IMAGE")
  try:
    record = get_safe_image(record_id)
    record = record[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[View Researcher Image] Record ID is invalid.')
    return redirect('search_records')

  Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_OK, details='View Record ' + str(record_id))

  filename = record.value
  
  response = HttpResponse()
  response['Content-Type'] = ''
  response['X-Accel-Redirect'] = '/media/images/%s' % filename
  return response

def researcher_video(request, record_id):
  """
  Serves a single anonymised medical record file.
  """
  try:
    record = get_safe_video(record_id)
    record = record[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[View Researcher Video] Record ID is invalid.')
    return redirect('search_records')

  Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_OK, details='View Record ' + str(record_id))

  filename = record.value

  response = HttpResponse()
  response['Content-Type'] = ''
  response['X-Accel-Redirect'] = '/media/videos/%s' % filename
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

def get_safe_image(record_id):
  safeimages = SafeImages.objects.filter(id=record_id)
  return safeimages

def get_safe_video(record_id):
  safevideos = SafeVideos.objects.filter(id=record_id)
  return safevideos

def get_model(record):
  return record._meta.object_name