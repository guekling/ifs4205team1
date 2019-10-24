from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from patientrecords.forms import ReadingsPermissionEditForm, TimeSeriesPermissionEditForm, DocumentsPermissionEditForm, VideosPermissionEditForm, ImagesPermissionEditForm

from core.models import Patient
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, ReadingsPerm, TimeSeriesPerm, DocumentsPerm, ImagesPerm, VideosPerm
from userlogs.models import Logs

from itertools import chain

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
    'permissions': permissions
  }

  return render(request, 'show_record.html', context)

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