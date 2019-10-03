from django.core.management import BaseCommand, call_command
from core.models import User, Patient

class Command(BaseCommand):
  help = "DEV COMMAND: Seed database with a set of user data for testing and development purposes."

  def add_arguments(self, parser):
    parser.add_argument('--fixturename', type=str)

  def handle(self, *args, **options):
    fixture_name = options['fixturename']
    call_command('loaddata', fixture_name) # Load JSON file to create users
    print("Loading of data completed.")
    # fix_passwords()
    # print("Fixing of passwords completed.")

def fix_passwords():
  """
  Hash the passwords of fixtures
  """
  for user in User.objects.all():
    print("{}{}".format("Fixing password for ", user))
    user.set_password(user.password)
    user.save()
  