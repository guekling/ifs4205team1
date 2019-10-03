import random

from django.core.management import BaseCommand
from core.models import User, Patient, Healthcare
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, ReadingsPerm, TimeSeriesPerm, DocumentsPerm, ImagesPerm, VideosPerm, Diagnosis, DiagnosisPerm

class Command(BaseCommand):
  help = "DEV COMMAND: Seed database with a generated set of medical records data for testing and development purposes."

  def handle(self, *args, **options):
    generate_timeseries_records()

def generate_timeseries_records():
  """
  Generate timeseries records for some patients
  """

  # Each patient can have 1..5 timeseries records
  random_number = generate_random_number(1, 5, 1)

  for p, patient in enumerate(Patient.objects.all().iterator()):
    print("{}{}".format("Generating timeseries records for patient ", patient))

    # Get all patient's healthcare professional
    patient_healthcare = patient.healthcare_patients.all()

    temp = 1
    while temp <= random_number[0]:
      data_path =  "{}{}{}".format("timeseries/TimeSeriesData", temp, ".txt")
      timeseries = TimeSeries.objects.create(owner_id=patient.username, patient_id=patient, data=data_path)

      for healthcare in patient_healthcare.iterator():
        TimeSeriesPerm.objects.create(timeseries_id=timeseries, username=healthcare, given_by=patient.username, perm_value=2)

      temp += 1

    if (p == 3999): # Generate timeseries records for 3,999 patients
      break

def generate_random_number(start, end, n):
  """
  Outputs a list of `n` generated numbers from `start` to `end`
  """

  result = [] 
  
  for i in range(n): 
    result.append(random.randint(start, end)) 
  
  return result