import csv
import random

from django.core.management import BaseCommand
from core.models import User, Patient, Healthcare
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, ReadingsPerm, TimeSeriesPerm, DocumentsPerm, ImagesPerm, VideosPerm, Diagnosis, DiagnosisPerm

class Command(BaseCommand):
  help = "DEV COMMAND: Seed database with a generated set of medical records data for testing and development purposes."

  def add_arguments(self, parser):
    parser.add_argument('--csvpath', type=str)

  def handle(self, *args, **options):
    path = options['csvpath']
    # generate_readings_records(path)
    # generate_diagnosis_records(path)
    # generate_images_records(path)
    generate_videos_records(path)
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

def generate_images_records(path):
  """
  Load CSV to populate `Images` & `ImagesPerm` table with data
  """
  with open(path, 'rt') as csvFile:
    reader = csv.reader(csvFile, delimiter=',', quotechar="\"")
    fields_name = next(reader)
    for r, row in enumerate(reader):
      image = Images()

      if (r < 6000): # Images 1 - 6000 to Patients 1 - 6000
        temp_r = r
      elif (r >= 6000) and (r < 12000): # Images 6001 - 12000 to Patients 1 - 6000
        temp_r = r - 6000
      elif (r >= 12000) and (r < 13100): # Images 12001 - 13100 to Patients 1 - 1100
        temp_r = r - 12000

      # Cancer: 2 images
      # MRI: 32 images
      # Ultrasound: 2 images
      # Xray: 2 images

      cancer_random_number = generate_random_number(1, 2, 1)
      mri_random_number = generate_random_number(1, 27, 1)
      ultrasound_random_number = generate_random_number(1, 2, 1)
      xray_random_number = generate_random_number(1, 2, 1)

      # type,title,time
      # Cancer,Cancer_bone,2017-11-15T11:28

      for i, field in enumerate(row):
        print("{}{}".format("Currently processing ", fields_name[i]))
        print("{}{}".format("Currently processing ", field))
        setattr(image, fields_name[i], field)
        
        if fields_name[i] == 'type':
          if field == 'Cancer':
            data_path = "{}{}{}".format("images/CANCER_Image_", cancer_random_number[0], ".jpg")
            image.data.name = data_path

          elif field == 'MRI':
            data_path = "{}{}{}".format("images/MRI_Image_", mri_random_number[0], ".jpg")
            image.data.name = data_path

          elif field == 'Ultrasound':
            data_path = "{}{}{}".format("images/ULTRASOUND_Image_", ultrasound_random_number[0], ".jpg")
            image.data.name = data_path

          elif field == 'Xray':
            data_path = "{}{}{}".format("images/XRAY_Image_", xray_random_number[0], ".jpg")
            image.data.name = data_path
        
        # Assign Images to a specific User & Patient
        patient = Patient.objects.all()[temp_r]
        user = patient.username
        image.owner_id = user
        image.patient_id = patient 

      image.save()
      print("{}{}{}".format("Image ", r, " is saved."))

      # Get all patient's healthcare professional
      patient_healthcare = patient.healthcare_patients.all()

      # Assign permissions to Healthcare
      for healthcare in patient_healthcare.iterator():
        perm = ImagesPerm.objects.create(img_id=image, given_by=user, perm_value=2)
        perm.username.add(healthcare)
      print("{}{}".format("Finishing processing permissions for image ", r))

def generate_videos_records(path):
  """
  Load CSV to populate `Videos` & `VideosPerm` table with data
  """
  with open(path, 'rt') as csvFile:
    reader = csv.reader(csvFile, delimiter=',', quotechar="\"")
    fields_name = next(reader)
    for r, row in enumerate(reader):
      video = Videos()

      if (r < 2000): # Videos 1 - 2000 to Patients 1 - 2000
        temp_r = r

      gastroscope_random_number = generate_random_number(1, 1, 1)
      gait_random_number = generate_random_number(1, 2, 1)

      for i, field in enumerate(row):
        print("{}{}".format("Currently processing ", fields_name[i]))
        print("{}{}".format("Currently processing ", field))
        setattr(video, fields_name[i], field)
        
        if fields_name[i] == 'type':
          if field == 'Gastroscope':
            data_path = "{}{}{}".format("videos/gastroscope_video_", gastroscope_random_number[0], ".mp4")
            video.data.name = data_path

          elif field == 'Gait':
            data_path = "{}{}{}".format("videos/gait_video_", gait_random_number[0], ".mp4")
            video.data.name = data_path
        
        # Assign Videos to a specific User & Patient
        patient = Patient.objects.all()[temp_r]
        user = patient.username
        video.owner_id = user
        video.patient_id = patient 

      video.save()
      print("{}{}{}".format("Image ", r, " is saved."))

      # Get all patient's healthcare professional
      patient_healthcare = patient.healthcare_patients.all()

      # Assign permissions to Healthcare
      for healthcare in patient_healthcare.iterator():
        perm = VideosPerm.objects.create(videos_id=video, given_by=user, perm_value=2)
        perm.username.add(healthcare)
      print("{}{}".format("Finishing processing permissions for video ", r))

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