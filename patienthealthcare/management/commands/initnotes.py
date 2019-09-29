from django.core.management import BaseCommand, call_command
from patientrecords.models import Documents

""" Clear all data and creates new notes """
MODE_REFRESH = 'refresh'

""" Does not clear data and creates new notes """
MODE_NONE = 'none'

class Command(BaseCommand):
  help = "DEV COMMAND: Seed databasse with a set of patient records data for testing and development purposes."

  def add_arguments(self, parser):
    parser.add_argument('--mode', type=str, help="Mode")

  def handle(self, *args, **options):
    run_seed(self, options['mode'])
        
# Deletes all data from User table and their corresponding tables
def clear_data():
  Documents.objects.all().delete()

# Seed database based on mode
def run_seed(self, mode):
  if mode == MODE_REFRESH:
    clear_data()

  call_command('loaddata','initial_notes') # Load JSON file to create records