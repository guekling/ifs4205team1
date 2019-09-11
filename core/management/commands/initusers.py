from django.core.management import BaseCommand, call_command
from core.models import User, Patient

class Command(BaseCommand):
  help = "DEV COMMAND: Seed databasse with a set of user data for testing and development purposes."

  def handle(self, *args, **options):
    call_command('loaddata','initial_users') # Load JSON file to create users
    fix_passwords()

# Hash the passwords of fixtures
def fix_passwords():
  for user in User.objects.all():
    user.set_password(user.password)
    user.save()
  