from django.core.management import BaseCommand, call_command
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, Diagnosis

class Command(BaseCommand):
  help = "DEV COMMAND: Seed databasse with a set of patient records data for testing and development purposes."

  def add_arguments(self, parser):
    parser.add_argument('--fixturename', type=str)

  def handle(self, *args, **options):
    fixture_name = options['fixturename']
    call_command('loaddata', fixture_name)
