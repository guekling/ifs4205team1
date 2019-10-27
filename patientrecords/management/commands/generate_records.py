import csv
import random

from django.core.management import BaseCommand
from core.models import User, Patient, Healthcare
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, ReadingsPerm, TimeSeriesPerm, DocumentsPerm, ImagesPerm, VideosPerm, Diagnosis, DiagnosisPerm

class Command(BaseCommand):
  help = "DEV COMMAND: Seed database with a generated set of medical records data for testing and development purposes."

  def add_arguments(self, parser):
    parser.add_argument('--csvpath', type=str)

  def handle(self, *args, **options): # -csvpath /../files/diagnosis_random.csv
    path = options['csvpath']
    # generate_readings_records(path)
    generate_diagnosis_records(path)

    # generate_timeseries_records()

def generate_readings_records(path):
  """
  Load CSV to populate `Readings` & `ReadingsPerm` table with data
  """
  with open(path, 'rt') as csvFile:
    reader = csv.reader(csvFile, delimiter=',', quotechar="\"")
    fields_name = next(reader)
    for r, row in enumerate(reader):
      reading = Readings()

      if (r < 6000): # Readings 1 - 6000 to Patients 1 - 6000
        temp_r = r
      elif (r >= 6000) and (r < 12000): # Readings 6001 - 12000 to Patients 1 - 6000
        temp_r = r - 6000
      elif (r >= 12000) and (r < 18000): # Readings 12001 - 18000 to Patients 1 - 6000
        temp_r = r - 12000
      elif (r >= 18000) and (r < 24000): # Readings 18001 - 24000 to Patients 1 - 6000
        temp_r = r - 18000
      elif (r >= 24000) and (r < 30000): # Readings 24001 - 30000 to Patients 1 - 6000
        temp_r = r - 24000
      elif (r >= 30000) and (r < 36000): # Readings 30001 - 36000 to Patients 1 - 6000
        temp_r = r - 30000
      else: # Readings 36001 - 40000 to Patients 1 - 4000
        temp_r = r - 36000

      for i, field in enumerate(row):
        print("{}{}".format("Currently processing ", fields_name[i]))
        print("{}{}".format("Currently processing ", field))
        setattr(reading, fields_name[i], field)
        
        # Assign Readings to a specific User & Patient
        patient = Patient.objects.all()[temp_r]
        user = patient.username
        reading.owner_id = user
        reading.patient_id = patient 

      reading.save()
      print("{}{}{}".format("Reading ", r, " is saved."))

      # Get all patient's healthcare professional
      patient_healthcare = patient.healthcare_patients.all()

      # Assign permissions to Healthcare
      for healthcare in patient_healthcare.iterator():
        perm = ReadingsPerm.objects.create(readings_id=reading, given_by=user, perm_value=2)
        perm.username.add(healthcare)
      print("{}{}".format("Finishing processing permissions for reading ", r))

def generate_diagnosis_records(path):
  """
  Load CSV to populate `Diagnosis` & `DiagnosisPerm` table with data
  """
  with open(path, 'rt') as csvFile:
    reader = csv.reader(csvFile, delimiter=',', quotechar="\"")
    fields_name = next(reader)
    for r, row in enumerate(reader):
      diagnosis = Diagnosis()

      if (r < 6000): # Diagnosis 1 - 6000 to Patients 1 - 6000
        temp_d = r
      else: # Diagnosis 6001 - 7800 to Patients 1 - 1800
        temp_d = r - 6000

      for i, field in enumerate(row):
        print("{}{}".format("Currently processing ", fields_name[i]))
        print("{}{}".format("Currently processing ", field))
        setattr(diagnosis, fields_name[i], field)
        
        # Assign Diagnosis to a specific User & Patient
        patient = Patient.objects.all()[temp_d]
        user = patient.username
        diagnosis.owner_id = user
        diagnosis.patient_id = patient

      diagnosis.save()
      print("{}{}{}".format("Diagnosis ", r, " is saved."))

      # Get all patient's healthcare professional
      patient_healthcare = patient.healthcare_patients.all()

      # Assign permissions to Healthcare
      for healthcare in patient_healthcare.iterator():
        perm = DiagnosisPerm.objects.create(diag_id=diagnosis, given_by=user, perm_value=2)
        perm.username.add(healthcare)
      print("{}{}".format("Finishing processing permissions for diagnosis ", r))

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