from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from core.models import User
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos

from itertools import chain

class ShowAllRecordsTest(TestCase):
  fixtures = ['initial_users', 'initial_records']

  def setUp(self):
    pass

  def test_show_all_records_load(self):
    uid = User.objects.get(username='testpatient').uid
    response = self.client.get(reverse('show_all_records', args=[uid]))
    self.assertEquals(response.status_code, 200)
    self.assertTemplateUsed(response, 'show_all_records.html')

  def test_show_all_records_does_not_load(self): # TODO: To change after view changes
    incorrect_uid = 'fbd9e0d9-9a01-4809-be1c-c0bb8ba94fcd'
    response = self.client.get(reverse('show_all_records', args=[incorrect_uid]))
    self.assertEquals(response.status_code, 404)

  def test_context(self):
    uid = User.objects.get(username='testpatient').uid
    response = self.client.get(reverse('show_all_records', args=[uid]))
    
    patient = User.objects.get(username='testpatient').patient
    readings = Readings.objects.filter(patient_id=patient)
    timeseries = TimeSeries.objects.filter(patient_id=patient)
    documents = Documents.objects.filter(patient_id=patient)
    images = Images.objects.filter(patient_id=patient)
    videos = Videos.objects.filter(patient_id=patient)
    context = list(chain(readings, timeseries, documents, images, videos))

    self.assertEquals(response.context['results'], context)