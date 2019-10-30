from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponse

from patientrecords.forms import ReadingsPermissionEditForm, TimeSeriesPermissionEditForm, DocumentsPermissionEditForm, VideosPermissionEditForm, ImagesPermissionEditForm, CreateNewRecord, CreateReadingsRecord, CreateTimeSeriesRecord, CreateImagesRecord, CreateVideosRecord, CreateDocumentsRecord

from core.models import Patient
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, ReadingsPerm, TimeSeriesPerm, DocumentsPerm, ImagesPerm, VideosPerm
from userlogs.models import Logs

import os
from itertools import chain
from mimetypes import guess_type

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def show_all_records(request, patient_id):
  """
  List all medical records belonging to the patient
  """
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Show All Records] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  readings = Readings.objects.filter(patient_id=patient)
  timeseries = TimeSeries.objects.filter(patient_id=patient)
  documents = Documents.objects.filter(patient_id=patient)
  images = Images.objects.filter(patient_id=patient)
  videos = Videos.objects.filter(patient_id=patient)

  results = list(chain(readings, timeseries, documents, images, videos))

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='Show All Records')

  context = {
    'patient': patient,
    'results': results
  }

  return render(request, 'show_all_records.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def show_record(request, patient_id, record_id):
  """
  Show information of a single medical record, and the permissions of the medical record
  """
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Show Record] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  try:
    record = get_record(record_id)
    record = record[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Show Record] Record ID is invalid.')
    return redirect('show_all_records', patient_id=patient_id)

  # Path to view restricted record
  record_path = os.path.join(settings.PROTECTED_MEDIA_PATH, str(record_id))

  model = get_model(record)

  if (model == "Readings"):
    permissions = ReadingsPerm.objects.filter(readings_id=record_id)
  elif (model == "TimeSeries"):
    permissions = TimeSeriesPerm.objects.filter(timeseries_id=record_id)
  elif (model == "Documents"):
    permissions = DocumentsPerm.objects.filter(docs_id=record_id)
  elif (model == "Videos"):
    permissions = VideosPerm.objects.filter(videos_id=record_id)
  elif (model == "Images"):
    permissions = ImagesPerm.objects.filter(img_id=record_id)
  else:
    permissions = ReadingsPerm.objects.none()

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='Show Record ' + str(record_id))

  context = {
    'patient': patient,
    'record': record,
    'permissions': permissions,
    'record_path': record_path
  }

  return render(request, 'show_record.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def download_record(request, patient_id, record_id):
  """
  Download a single medical record
  """
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Download Record] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  try:
    record = get_record(record_id)
    record = record[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Download Record] Record ID is invalid.')
    return redirect('show_all_records', patient_id=patient_id)

  file_path = record.data.path
  file_name = record.data.name.split('/', 1)[1]

  with open(file_path, 'rb') as record:
    content_type = guess_type(file_path)[0]
    response = HttpResponse(record, content_type=content_type)
    response['Content-Length'] = os.path.getsize(file_path)
    response['Content-Disposition'] = "attachment; filename=%s" %  file_name

    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='Download Record ' + str(record_id))

    return response

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def edit_permission(request, patient_id, record_id, perm_id):
  """
  Edit a permission of a single medical record
  """
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Edit Permission] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  try:
    record = get_record(record_id)
    record = record[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Edit Permission] Record ID is invalid.')
    return redirect('show_all_records', patient_id=patient_id)

  model = get_model(record)

  if (model == "Readings"):
    permission = ReadingsPerm.objects.get(id = perm_id)
    form = ReadingsPermissionEditForm(request.POST or None, instance=permission)
    if request.method == 'POST':
      if form.is_valid():
        permission.save()
        Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='Edit Permission ' + str(perm_id))
        return redirect('show_record', patient_id=patient_id, record_id=record_id)
      else:
        Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Edit Permission] Invalid Form')
        context = {
          'form': form,
          'patient': patient,
          'record': record,
          'permission': permission
        }
        return render(request, 'edit_permission.html', context)
  elif (model == "TimeSeries"):
    permission = TimeSeriesPerm.objects.get(id = perm_id)
    form = TimeSeriesPermissionEditForm(request.POST or None, instance=permission)
    if request.method == 'POST':
      if form.is_valid():
        permission.save()
        Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='Edit Permission ' + str(perm_id))
        return redirect('show_record', patient_id=patient_id, record_id=record_id)
      else:
        Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Edit Permission] Invalid Form')
        context = {
          'form': form,
          'patient': patient,
          'record': record,
          'permission': permission
        }
        return render(request, 'edit_permission.html', context)
  elif (model == "Documents"):
    permission = DocumentsPerm.objects.get(id = perm_id)
    form = DocumentsPermissionEditForm(request.POST or None, instance=permission)
    if request.method == 'POST':
      if form.is_valid():
        permission.save()
        Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='Edit Permission ' + str(perm_id))
        return redirect('show_record', patient_id=patient_id, record_id=record_id)
      else:
        Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Edit Permission] Invalid Form')
        context = {
          'form': form,
          'patient': patient,
          'record': record,
          'permission': permission
        }
        return render(request, 'edit_permission.html', context)
  elif (model == "Videos"):
    permission = VideosPerm.objects.get(id = perm_id)
    form = VideosPermissionEditForm(request.POST or None, instance=permission)
    if request.method == 'POST':
      if form.is_valid():
        permission.save()
        Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='Edit Permission ' + str(perm_id))
        return redirect('show_record', patient_id=patient_id, record_id=record_id)
      else:
        Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Edit Permission] Invalid Form')
        context = {
          'form': form,
          'patient': patient,
          'record': record,
          'permission': permission
        }
        return render(request, 'edit_permission.html', context)
  elif (model == "Images"):
    permission = ImagesPerm.objects.get(id = perm_id)
    form = ImagesPermissionEditForm(request.POST or None, instance=permission)
    if request.method == 'POST':
      if form.is_valid():
        permission.save()
        Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='Edit Permission ' + str(perm_id))
        return redirect('show_record', patient_id=patient_id, record_id=record_id)
      else:
        Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Edit Permission] Invalid Form')
        context = {
          'form': form,
          'patient': patient,
          'record': record,
          'permission': permission
        }
        return render(request, 'edit_permission.html', context)
  else:
    permission = ReadingsPerm.objects.none()

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='[Edit Permission] Render Form')

  context = {
    'form': form,
    'patient': patient,
    'record': record,
    'permission': permission
  }

  return render(request, 'edit_permission.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def new_record(request, patient_id):
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[New Record] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  form = CreateNewRecord(request.POST)

  if request.method == 'POST':
    if form.is_valid():
      type = form.cleaned_data['type']

      if (type == 'Readings'):
        return redirect('new_readings_record', patient_id=patient_id)
      elif (type == 'TimeSeries'):
        return redirect('new_timeseries_record', patient_id=patient_id)
      elif (type == 'Images'):
        return redirect('new_images_record', patient_id=patient_id)
      elif (type == 'Videos'):
        return redirect('new_videos_record', patient_id=patient_id)
      elif (type == 'Documents'):
        return redirect('new_documents_record', patient_id=patient_id)

      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='New Record')
    else:
      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[New Record] Invalid Form')

      context = {
        'form': form,
        'patient': patient,
      }

      return render(request, 'new_record.html', context)

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='[New Record] Render Form')

  context = {
    'form': form,
    'patient': patient,
  }

  return render(request, 'new_record.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def new_readings_record(request, patient_id):
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[New Readings Record] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  form = CreateReadingsRecord(request.POST or None)

  if request.method == 'POST':
    if form.is_valid():
      readings = form.save(commit=False)
      readings.owner_id = patient.username
      readings.patient_id = patient
      type = form.cleaned_data['type']
      readings.type = type
      readings.save()

      # Get all patient's healthcare professional
      patient_healthcare = patient.healthcare_patients.all()

      for healthcare in patient_healthcare:
        permission = ReadingsPerm.objects.create(readings_id=readings, given_by=patient.username, perm_value=2)
        permission.username.add(healthcare)
      
      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='New Readings Record')
      return redirect('show_record', patient_id=patient_id, record_id=readings.id)
    else:
      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[New Readings Record] Invalid Form')
      context = {
        'form': form,
        'patient': patient,
      }
      return render(request, 'new_readings_record.html', context)

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='[New Readings Record] Render Form')

  context = {
    'form': form,
    'patient': patient,
  }

  return render(request, 'new_readings_record.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def new_timeseries_record(request, patient_id):
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[New TimeSeries Record] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  form = CreateTimeSeriesRecord(request.POST or None, request.FILES)

  if request.method == 'POST':
    if form.is_valid():
      timeseries = form.save(commit=False)
      timeseries.owner_id = patient.username
      timeseries.patient_id = patient
      timeseries.save()

      # Get all patient's healthcare professional
      patient_healthcare = patient.healthcare_patients.all()

      for healthcare in patient_healthcare:
        permission = TimeSeriesPerm.objects.create(timeseries_id=timeseries, given_by=patient.username, perm_value=2)
        permission.username.add(healthcare)
      
      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='New TimeSeries Record')
      return redirect('show_record', patient_id=patient_id, record_id=timeseries.id)
    else:
      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[New TimeSeries Record] Invalid Form')
      context = {
        'form': form,
        'patient': patient,
      }
      return render(request, 'new_timeseries_record.html', context)

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='[New TimeSeries Record] Render Form')

  context = {
    'form': form,
    'patient': patient,
  }

  return render(request, 'new_timeseries_record.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def new_images_record(request, patient_id):
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[New Images Record] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  form = CreateImagesRecord(request.POST or None, request.FILES)

  if request.method == 'POST':
    if form.is_valid():
      images = form.save(commit=False)
      images.owner_id = patient.username
      images.patient_id = patient
      type = form.cleaned_data['type']
      images.type = type
      images.save()

      # Get all patient's healthcare professional
      patient_healthcare = patient.healthcare_patients.all()

      for healthcare in patient_healthcare:
        permission = ImagesPerm.objects.create(img_id=images, given_by=patient.username, perm_value=2)
        permission.username.add(healthcare)
      
      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='New Images Record')
      return redirect('show_record', patient_id=patient_id, record_id=images.id)
    else:
      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[New Images Record] Invalid Form')
      context = {
        'form': form,
        'patient': patient,
      }
      return render(request, 'new_images_record.html', context)

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='[New Images Record] Render Form')

  context = {
    'form': form,
    'patient': patient,
  }

  return render(request, 'new_images_record.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def new_videos_record(request, patient_id):
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[New Videos Record] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  form = CreateVideosRecord(request.POST or None, request.FILES)

  if request.method == 'POST':
    if form.is_valid():
      videos = form.save(commit=False)
      videos.owner_id = patient.username
      videos.patient_id = patient
      type = form.cleaned_data['type']
      videos.type = type
      videos.save()

      # Get all patient's healthcare professional
      patient_healthcare = patient.healthcare_patients.all()

      for healthcare in patient_healthcare:
        permission = VideosPerm.objects.create(videos_id=videos, given_by=patient.username, perm_value=2)
        permission.username.add(healthcare)
      
      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='New Videos Record')
      return redirect('show_record', patient_id=patient_id, record_id=videos.id)
    else:
      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[New Videos Record] Invalid Form')
      context = {
        'form': form,
        'patient': patient,
      }
      return render(request, 'new_videos_record.html', context)

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='[New Videos Record] Render Form')

  context = {
    'form': form,
    'patient': patient,
  }

  return render(request, 'new_videos_record.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def new_documents_record(request, patient_id):
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[New Documents Record] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  form = CreateDocumentsRecord(request.POST or None, request.FILES)

  if request.method == 'POST':
    if form.is_valid():
      docs = form.save(commit=False)
      docs.owner_id = patient.username
      docs.patient_id = patient
      type = form.cleaned_data['type']
      docs.type = type
      docs.save()

      # Get all patient's healthcare professional
      patient_healthcare = patient.healthcare_patients.all()

      for healthcare in patient_healthcare:
        permission = DocumentsPerm.objects.create(docs_id=docs, given_by=patient.username, perm_value=2)
        permission.username.add(healthcare.username)
      
      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='New Documents Record')
      return redirect('show_record', patient_id=patient_id, record_id=docs.id)
    else:
      Logs.objects.create(type='UPDATE', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[New Documents Record] Invalid Form')
      context = {
        'form': form,
        'patient': patient,
      }
      return render(request, 'new_documents_record.html', context)

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='[New Documents Record] Render Form')

  context = {
    'form': form,
    'patient': patient,
  }

  return render(request, 'new_documents_record.html', context)

##########################################
############ Helper Functions ############
##########################################

STATUS_OK = 1
STATUS_ERROR = 0

def patient_does_not_exists(patient_id): # TODO: This function is never called?
  """
  Redirects to login if patient_id is invalid
  """
  try:
    return Patient.objects.get(id=patient_id)
  except Patient.DoesNotExist:
    Logs.objects.create(type='READ', user_id=patient_id, interface='PATIENT', status=STATUS_ERROR, details='Patient ID is invalid.')
    redirect('patient_login')

def get_record(record_id):
  readings = Readings.objects.filter(id=record_id)
  timeseries = TimeSeries.objects.filter(id=record_id)
  documents = Documents.objects.filter(id=record_id)
  images = Images.objects.filter(id=record_id)
  videos = Videos.objects.filter(id=record_id)

  return list(chain(readings, timeseries, documents, images, videos))

def get_model(record):
  return record._meta.object_name