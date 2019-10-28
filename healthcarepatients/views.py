from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponse

from healthcarepatients.forms import TransferPatientForm

from core.models import Healthcare
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, ReadingsPerm, TimeSeriesPerm, DocumentsPerm, ImagesPerm, VideosPerm
from userlogs.models import Logs

import os
from itertools import chain
from mimetypes import guess_type

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def show_all_patients(request, healthcare_id):
  """
  List all patients the healthcare professional has
  """ 
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show All Patients] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  patients = healthcare.patients.all()

  Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='Show All Patients')

  context = {
    'healthcare': healthcare,
    'patients': patients
  }

  return render(request, 'show_all_patients.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def show_patient(request, healthcare_id, patient_id):
  """
  Show information of a single patient
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show Patient] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    patient = healthcare.patients.all().filter(id=patient_id)
    patient = patient[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show Patient] Patient ID is invalid.')
    return redirect('show_all_patients', healthcare_id=healthcare_id)

  Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='Show Patient ' + str(patient_id))

  context = {
    'healthcare': healthcare,
    'patient': patient,
  }

  return render(request, 'show_patient.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def show_patient_records(request, healthcare_id, patient_id):
  """
  List all medical records belonging to a single patient
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show Patient Records] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))

    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    patient = healthcare.patients.all().filter(id=patient_id)
    patient = patient[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show Patient] Patient ID is invalid.')
    return redirect('show_all_patients', healthcare_id=healthcare_id)

  records = get_records(patient)

  context = {
    'healthcare': healthcare,
    'patient': patient,
    'records': records,
  }

  Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='Show Patient ' + str(patient_id) + ' Records')

  return render(request, 'show_patient_records.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def show_patient_record(request, healthcare_id, patient_id, record_id):
  """
  Show information of a single record belonging to a single patient
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show Patient Record] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    patient = healthcare.patients.all().filter(id=patient_id)
    patient = patient[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show Patient Record] Patient ID is invalid.')
    return redirect('show_all_patients', healthcare_id=healthcare_id)

  try:
    record = get_record(record_id)
    record = record[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show Patient Record] Record ID is invalid.')
    return redirect('show_patient_records', healthcare_id=healthcare_id, patient_id=patient_id)

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

  context = {
    'healthcare': healthcare,
    'patient': patient,
    'record': record,
    'permissions': permissions
  }

  Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='Show Patient ' + str(patient_id) + ' Record ' + str(record_id))

  return render(request, 'show_patient_record.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def download_patient_record(request, healthcare_id, patient_id, record_id):
  """
  Download a single medical record
  """
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Download Patient Record] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    patient = healthcare.patients.all().filter(id=patient_id)
    patient = patient[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Download Patient Record] Patient ID is invalid.')
    return redirect('show_all_patients', healthcare_id=healthcare_id)

  try:
    record = get_record(record_id)
    record = record[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Download Patient Record] Record ID is invalid.')
    return redirect('show_patient_records', healthcare_id=healthcare_id, patient_id=patient_id)

  file_path = record.data.path
  file_name = record.data.name.split('/', 1)[1]

  with open(file_path, 'rb') as record:
    content_type = guess_type(file_path)[0]
    response = HttpResponse(record, content_type=content_type)
    response['Content-Length'] = os.path.getsize(file_path)
    response['Content-Disposition'] = "attachment; filename=%s" %  file_name

    Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='Download Patient ' + str(patient_id) + ' Record ' + str(record_id))

    return response

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def transfer_patient(request, healthcare_id, patient_id):
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Transfer Patient] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))

    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    patient = healthcare.patients.all().filter(id=patient_id)
    patient = patient[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Transfer Patient] Patient ID is invalid.')
    return redirect('show_all_patients', healthcare_id=healthcare_id)

  form = TransferPatientForm(request.POST)

  if request.method == 'POST':
    if form.is_valid():
      transfer_healthcare = form.cleaned_data['healthcare_professional']
      patient.healthcare_patients.add(transfer_healthcare) # Does not do anything even if healthcare professional chosen is already tagged to patient

      # Set default permissions for patient's medical records for new Healthcare
      healthcare_user = healthcare.username
      records = get_records(patient)

      for record in records:
        model = get_model(record)
        
      if (model == "Readings"):
        permission = ReadingsPerm.objects.create(readings_id=record, given_by=healthcare_user, perm_value=2)
        permission.username.add(transfer_healthcare)
      elif (model == "TimeSeries"):
        permission = TimeSeriesPerm.objects.create(timeseries_id=record, given_by=healthcare_user, perm_value=2)
        permission.username.add(transfer_healthcare)
      elif (model == "Documents"):
        permission = DocumentsPerm.objects.create(docs_id=record, given_by=healthcare_user, perm_value=2)
        permission.username.add(transfer_healthcare.username)
      elif (model == "Videos"):
        permission = VideosPerm.objects.create(videos_id=record, given_by=healthcare_user, perm_value=2)
        permission.username.add(transfer_healthcare)
      elif (model == "Images"):
        permission = ImagesPerm.objects.create(img_id=record, given_by=healthcare_user, perm_value=2)
        permission.username.add(transfer_healthcare)

      Logs.objects.create(type='UPDATE', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='Transfer Patient ' + str(patient_id) + ' to Healthcare Prof ' + str(transfer_healthcare.id))

      return redirect('show_patient', healthcare_id=healthcare_id, patient_id=patient_id)
    else:
      Logs.objects.create(type='UPDATE', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Transfer Patient] Invalid Form')
      context = {
        'form': form,
        'patient': patient,
        'healthcare': healthcare,
      }
      return render(request, 'show_patient.html', context)

  Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Transfer Patient] Render Form')

  context = {
    'form': form,
    'patient': patient,
    'healthcare': healthcare,
  }

  return render(request, 'transfer_patient.html', context)

##########################################
############ Helper Functions ############
##########################################

STATUS_OK = 1
STATUS_ERROR = 0

def healthcare_does_not_exists(healthcare_id): # TODO: This function is never called?
  """
  Redirects to login if healthcare_id is invalid
  """
  try:
    return Healthcare.objects.get(id=healthcare_id)
  except Healthcare.DoesNotExist:
    redirect('healthcare_login')

def get_records(patient):
  """
  Retrieve all records of a single patient
  """
  readings = Readings.objects.filter(patient_id=patient)
  timeseries = TimeSeries.objects.filter(patient_id=patient)
  documents = Documents.objects.filter(patient_id=patient)
  images = Images.objects.filter(patient_id=patient)
  videos = Videos.objects.filter(patient_id=patient)

  return list(chain(readings, timeseries, documents, images, videos))

def get_record(record_id):
  """
  Retrieve a single record
  """
  readings = Readings.objects.filter(id=record_id)
  timeseries = TimeSeries.objects.filter(id=record_id)
  documents = Documents.objects.filter(id=record_id)
  images = Images.objects.filter(id=record_id)
  videos = Videos.objects.filter(id=record_id)

  return list(chain(readings, timeseries, documents, images, videos))

def get_model(record):
  return record._meta.object_name
