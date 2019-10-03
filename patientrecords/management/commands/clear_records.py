from django.core.management import BaseCommand
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, Diagnosis

class Command(BaseCommand):
  help = "DEV COMMAND: Clear all medical records data."

  def handle(self, *args, **options):
    clear_all()
        
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