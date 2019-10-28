from django.core.management import BaseCommand, call_command
from researcherquery.models import QiInfo, SafeUsers, SafeDiagnosis, SafeReadings

class Command(BaseCommand):
  help = "DEV COMMAND: Seed database with a set of safe records for testing and development purposes."

  def handle(self, *args, **options):
    fixture_name = 'researcherquery/fixtures/initial_saferecords.json'
    database_name = 'safedb'
    # call_command('loaddata', fixture_name, app_label=app_name, database=database_name) # Load JSON file to create safe records
    
    call_command('loaddata', fixture_name, '--database', database_name) # Load JSON file to create safe records

    print("Loading of data completed.")