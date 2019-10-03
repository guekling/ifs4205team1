from django.core.management import BaseCommand
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, Diagnosis

MODEL_ALL = 'all'

MODEL_READINGS = 'readings'
MODEL_TIMESERIES = 'timeseries'
MODEL_DOCUMENTS = 'documents'
MODEL_IMAGES = 'images'
MODEL_VIDEOS = 'videos'
MODEL_DIAGNOSIS = 'diagnosis'

class Command(BaseCommand):
  help = "DEV COMMAND: Clear all medical records data."

  def add_arguments(self, parser):
    parser.add_argument('--model', type=str)

  def handle(self, *args, **options):
    run(self, options['model'])
        
def clear_all():
  """
  Deletes all medical records data
  """
  Readings.objects.all().delete()
  TimeSeries.objects.all().delete()
  Documents.objects.all().delete()
  Images.objects.all().delete()
  Videos.objects.all().delete()
  Diagnosis.objects.all().delete()

def run(self, model):
  if model == MODEL_ALL:
    clear_all()
  elif model == MODEL_READINGS:
    Readings.objects.all().delete()
  elif model == MODEL_TIMESERIES:
    TimeSeries.objects.all().delete()
  elif model == MODEL_DOCUMENTS:
    Documents.objects.all().delete()
  elif model == MODEL_IMAGES:
    Images.objects.all().delete()
  elif model == MODEL_VIDEOS:
    Videos.objects.all().delete()
  else:
    Diagnosis.objects.all().delete()