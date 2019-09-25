from django.http import Http404 # TODO: Remove when not in use
from django.shortcuts import render, redirect

from patientrecords.forms import ReadingsPermissionEditForm

from core.models import Patient
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, ReadingsPerm, TimeSeriesPerm, DocumentsPerm, ImagesPerm, VideosPerm

from itertools import chain

def show_all_records(request, patient_id):
  """
  List all medical records belonging to the patient
  """

  patient = check_patient_exists(patient_id)

  readings = Readings.objects.filter(patient_id=patient)
  timeseries = TimeSeries.objects.filter(patient_id=patient)
  documents = Documents.objects.filter(patient_id=patient)
  images = Images.objects.filter(patient_id=patient)
  videos = Videos.objects.filter(patient_id=patient)

  results = list(chain(readings, timeseries, documents, images, videos))

  context = {
    'results': results
  }

  return render(request, 'show_all_records.html', context)

def show_record(request, patient_id, record_id):
  """
  Show information of a single medical record
  """

  patient = check_patient_exists(patient_id)

  try:
    record = get_record(record_id)
    record = record[0]
  except IndexError:
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

  context = {
    'record': record,
    'permissions': permissions
  }

  return render(request, 'show_record.html', context)

def edit_permission(request, patient_id, record_id, perm_id):
  """
  Edit a permission of a single medical record
  """

  patient = check_patient_exists(patient_id)

  try:
    record = get_record(record_id)
    record = record[0]
  except IndexError:
    return redirect('show_all_records', patient_id=patient_id)

  model = get_model(record)

  if (model == "Readings"):
    permission = ReadingsPerm.objects.get(id = perm_id)
    form = ReadingsPermissionEditForm(request.POST or None, instance=permission)
    if request.method == 'POST':
      if form.is_valid():
        permission.save()
        return redirect('show_record', patient_id=patient_id, record_id=record_id)
      else:
        context = {
          'form': form,
          'patient': patient,
          'record': record,
          'permission': permission
        }
        return render(request, 'edit_permission.html', context)
  elif (model == "TimeSeries"):
    permissions = TimeSeriesPerm.objects.filter(id = perm_id)
    form = TimeSeriesPermissionEditForm(request.POST or None, instance=permission)
    if request.method == 'POST':
      if form.is_valid():
        permission.save()
        return redirect('show_record', patient_id=patient_id, record_id=record_id)
      else:
        context = {
          'form': form,
          'patient': patient,
          'record': record,
          'permission': permission
        }
        return render(request, 'edit_permission.html', context)
  elif (model == "Documents"):
    permissions = DocumentsPerm.objects.filter(id = perm_id)
    form = DocumentsPermissionEditForm(request.POST or None, instance=permission)
    if request.method == 'POST':
      if form.is_valid():
        permission.save()
        return redirect('show_record', patient_id=patient_id, record_id=record_id)
      else:
        context = {
          'form': form,
          'patient': patient,
          'record': record,
          'permission': permission
        }
        return render(request, 'edit_permission.html', context)
  elif (model == "Videos"):
    permissions = VideosPerm.objects.filter(id = perm_id)
    form = VideosEditForm(request.POST or None, instance=permission)
    if request.method == 'POST':
      if form.is_valid():
        permission.save()
        return redirect('show_record', patient_id=patient_id, record_id=record_id)
      else:
        context = {
          'form': form,
          'patient': patient,
          'record': record,
          'permission': permission
        }
        return render(request, 'edit_permission.html', context)
  elif (model == "Images"):
    permissions = ImagesPerm.objects.filter(id = perm_id)
    form = ImagesEditForm(request.POST or None, instance=permission)
    if request.method == 'POST':
      if form.is_valid():
        permission.save()
        return redirect('show_record', patient_id=patient_id, record_id=record_id)
      else:
        context = {
          'form': form,
          'patient': patient,
          'record': record,
          'permission': permission
        }
        return render(request, 'edit_permission.html', context)
  else:
    permissions = ReadingsPerm.objects.none()

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

def check_patient_exists(patient_id):
  try:
    return Patient.objects.get(id=patient_id)
  except Patient.DoesNotExist:
    raise Http404("Patient does not exist") # TODO: Redirects to login page

def get_record(record_id):
  readings = Readings.objects.filter(id=record_id)
  timeseries = TimeSeries.objects.filter(id=record_id)
  documents = Documents.objects.filter(id=record_id)
  images = Images.objects.filter(id=record_id)
  videos = Videos.objects.filter(id=record_id)

  return list(chain(readings, timeseries, documents, images, videos))

def get_model(record):
  return record._meta.object_name