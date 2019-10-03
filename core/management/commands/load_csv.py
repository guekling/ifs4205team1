import csv
from django.core.management import BaseCommand
from core.models import User

class Command(BaseCommand):
  help = "DEV COMMAND: Seed databasse with a set of user data from a CSV file for testing and development purposes."

  def add_arguments(self, parser):
    parser.add_argument('--csvpath', type=str)

  def handle(self, *args, **options):
    path = options['csvpath']
    load_csv(path)

def load_csv(path):
  '''
  Load CSV to populate database `User` with users
  '''
  with open(path, 'rt') as csvFile:
    reader = csv.reader(csvFile, delimiter=',', quotechar="\"")
    fields_name = next(reader)

    for row in reader:
      user = User()
      for i, field in enumerate(row):
        if fields_name != "password":
          setattr(user, fields_name[i], field)
        else:
          user.set_password(password)
      user.save()