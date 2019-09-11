from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from core.models import User

class ShowAllRecordsTest(TestCase):
  fixtures = ['initial_users', 'initial_records']

  def setUp(self):
    pass

  def test_show_all_records_load(self):
    uid = User.objects.get(username='testpatient').uid
    response = self.client.get(reverse('show_all_records', args=[uid]))
    self.assertEquals(response.status_code, 200)
    self.assertTemplateUsed(response, 'show_all_records.html')