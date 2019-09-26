from django.core.management import call_command
from django.test import TestCase, Client
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from core.models import User, Patient
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos

from itertools import chain

class ShowAllRecordsTest(TestCase):
  fixtures = ['initial_users', 'initial_records']

  def setUp(self):
    user = User.objects.get(username='testpatient')
    user.set_password('1234')
    user.save()

    self.client.login(username='testpatient', password='1234')

  def test_show_all_records_load(self):
    patient_id = User.objects.get(username='testpatient').patient.id
    response = self.client.get(reverse('show_all_records', args=[patient_id]))
    self.assertEquals(response.status_code, 200)
    self.assertTemplateUsed(response, 'show_all_records.html')

  def test_incorrect_patient_id_when_login_show_all_records_does_not_load(self):
    incorrect_patient_id = 'fbd9e0d9-9a01-4809-be1c-c0bb8ba94fcd'
    with self.assertRaises(NoReverseMatch): # unable to redirect to dashboard after being redirected to login
      self.client.get(reverse('show_all_records', args=[incorrect_patient_id]))

  def test_incorrect_patient_id_when_not_login_show_all_records_redirect(self):
    self.client.logout()
    incorrect_patient_id = 'fbd9e0d9-9a01-4809-be1c-c0bb8ba94fcd'
    response = self.client.get(reverse('show_all_records', args=[incorrect_patient_id]))
    self.assertEquals(response.status_code, 302)

  def test_context(self):
    patient_id = User.objects.get(username='testpatient').patient.id
    response = self.client.get(reverse('show_all_records', args=[patient_id]))
    
    patient = User.objects.get(username='testpatient').patient
    readings = Readings.objects.filter(patient_id=patient)
    timeseries = TimeSeries.objects.filter(patient_id=patient)
    documents = Documents.objects.filter(patient_id=patient)
    images = Images.objects.filter(patient_id=patient)
    videos = Videos.objects.filter(patient_id=patient)
    context = list(chain(readings, timeseries, documents, images, videos))

    self.assertEquals(response.context['results'], context)