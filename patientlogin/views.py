from django.shortcuts import render, redirect

from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView

from core.models import Patient
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, ReadingsPerm, TimeSeriesPerm, DocumentsPerm, ImagesPerm, VideosPerm

class PatientLogin(LoginView):
  """
  Custom patient login view that extends from Django's LoginView
  """
  form_class = AuthenticationForm
  template_name = 'patient_login.html'

  def form_valid(self, form):
    """
    Checks if a user is a patient
    """
    try:
      patient = form.get_user().patient
    except Patient.DoesNotExist:
      patient = None

    if patient is not None:
      auth_login(self.request, form.get_user())
      return redirect('patient_dashboard', patient_id=patient.id)
    else:
      form = AuthenticationForm

      context = {
        'form': form,
      }

      return render(self.request, 'patient_login.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient, login_url='/patient/login/')
def patient_dashboard(request, patient_id):
  patient = Patient.objects.get(id=patient_id)

  context = {
    'patient': patient,
  }

  return render(request, 'patient_dashboard.html', context)