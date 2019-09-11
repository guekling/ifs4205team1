from django.shortcuts import render
from core.models import User
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos

from itertools import chain

# List all medical records belonging to the patient
def show_all_records(request, uid):
  patient = User.objects.get(uid=uid).patient

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