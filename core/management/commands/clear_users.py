from django.core.management import BaseCommand
from core.models import User, Patient, Admin, Healthcare, Researcher

class Command(BaseCommand):
  help = "DEV COMMAND: Clear all user data."

  def handle(self, *args, **options):
    clear_all()
        
def clear_all():
  """
  Deletes all user data. 
  """
  Healthcare.objects.all().delete()
  Patient.objects.all().delete()
  Admin.objects.all().delete()
  Researcher.objects.all().delete()
  User.objects.all().delete()