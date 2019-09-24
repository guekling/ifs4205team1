from django.http import Http404 # TODO: Remove when not in use
from django.shortcuts import render, redirect

from core.models import Patient
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, ReadingsPerm, TimeSeriesPerm, DocumentsPerm, ImagesPerm, VideosPerm

from itertools import chain

# List all medical records belonging to the patient
def show_all_records(request, patient_id):
  try:
    patient = Patient.objects.get(id=patient_id)
  except Patient.DoesNotExist:
    raise Http404("Patient does not exist") # TODO: Redirects to login page

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

# Show information of a single medical record
def show_record(request, patient_id, record_id):
  try:
    patient = Patient.objects.get(id=patient_id)
  except Patient.DoesNotExist:
    raise Http404("Patient does not exist") # TODO: Redirects to login page

  try:
    readings = Readings.objects.filter(id=record_id)
    timeseries = TimeSeries.objects.filter(id=record_id)
    documents = Documents.objects.filter(id=record_id)
    images = Images.objects.filter(id=record_id)
    videos = Videos.objects.filter(id=record_id)

    record = list(chain(readings, timeseries, documents, images, videos))
    record = record[0]
  except IndexError:
    return redirect('show_all_records', patient_id=patient_id)

  model = record._meta.object_name

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

