import csv
import random

from django.core.management import BaseCommand
from core.models import User, Patient, Healthcare, Researcher, Admin

class Command(BaseCommand):
  help = "DEV COMMAND: Seed database with a set of user data from a CSV file for testing and development purposes."

  def add_arguments(self, parser):
    parser.add_argument('--csvpath', type=str)

  def handle(self, *args, **options):
    path = options['csvpath']
    load_csv(path)
    assign_patients()

def load_csv(path):
  """
  Load CSV to populate database `User` with users
  """
  with open(path, 'rt') as csvFile:
    reader = csv.reader(csvFile, delimiter=',', quotechar="\"")
    fields_name = next(reader)

    for r, row in enumerate(reader):
      user = User()
      for i, field in enumerate(row):
        print("{}{}".format("Currently processing ", fields_name[i]))
        print("{}{}".format("Currently processing ", field))
        setattr(user, fields_name[i], field)
      user.save()
      user.set_password(user.password)
      user.save()
      print("{}{}{}".format("User ", user, " is saved."))

      # Assign Users to a specific role
      if (r < 6000): # Users 1 - 6000
        Patient.objects.create(username=user)
      elif (r >= 6000) and (r < 8000): # Users 6001 - 8000
        Healthcare.objects.create(username=user, license=user.postalcode)
      elif (r >= 8000) and (r < 9059): # Users 8000 - 9059
        Researcher.objects.create(username=user)
      else: # User 9060
        Admin.objects.create(username=user)

def assign_patients():
  """
  Assign patients to healthcare professionals
  """

  for healthcare in Healthcare.objects.all():
    print("{}{}".format("Assigning patients for healthcare professional ", healthcare))
    # Each healthcare professional can have 5..100 patients
    random_number = generate_random_number(5, 100, 1)
    # Generate a list of numbers to be used to grab the respective patient objects
    random_list = generate_random_number(0, 5999, random_number[0])

    for i in random_list:
      patient = Patient.objects.all()[i]
      healthcare.patients.add(patient)

def generate_random_number(start, end, n):
  """
  Outputs a list of `n` generated numbers from `start` to `end`
  """

  result = [] 
  
  for i in range(n): 
    result.append(random.randint(start, end)) 
  
  return result