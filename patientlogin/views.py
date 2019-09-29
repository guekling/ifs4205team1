from django.shortcuts import render, redirect
from django.template import RequestContext
from django.urls import reverse_lazy

from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

from patientlogin.forms import UserEditForm

from core.models import User, Patient
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

class PatientLogout(LogoutView):
  """
  Custom patient logout view that extends from Django's LogoutView
  """
  next_page = '/patient/login'

class PatientChangePassword(PasswordChangeView):
  """
  Custom patient change password view that extends from Django's PasswordChangeView
  """
  form_class = PasswordChangeForm
  template_name = 'patient_change_password.html'

  def get_success_url(self):
    user = self.request.user
    print(user)
    url = reverse_lazy('patient_change_password_complete', kwargs={'patient_id': user.patient.id})
    return url
  #   url = self.get_redirect_url()
  #   return url or resolve_url(settings.LOGIN_REDIRECT_URL)

class PatientChangePasswordComplete(PasswordChangeDoneView):
  """
  Custom patient change password complete view that extends from Django's PasswordChangeDoneView
  """
  template_name = 'patient_change_password_complete.html'

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient, login_url='/patient/login/')
def patient_settings(request, patient_id):
  patient = patient_does_not_exists(patient_id)
  user = patient.username

  context = {
    'patient': patient,
    'user': user,
  }

  return render(request, 'patient_settings.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient, login_url='/patient/login/')
def patient_edit_settings(request, patient_id):
  patient = patient_does_not_exists(patient_id)
  user = patient.username
  form = UserEditForm(request.POST or None, instance=user)

  if request.method == 'POST':
    if form.is_valid():
      user.save()
      return redirect('patient_settings', patient_id=patient_id)
    else:
      context = {
        'form': form,
        'patient': patient,
        'user': user,
      }
      return render(request, 'patient_edit_settings.html', context)

  context = {
    'form': form,
    'patient': patient,
    'user': user,
  }

  return render(request, 'patient_edit_settings.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient, login_url='/patient/login/')
def patient_change_password(request, patient_id):
  patient = patient_does_not_exists(patient_id)

  change_password = PatientChangePassword.as_view(
    extra_context={'patient': patient}
  )

  return change_password(request)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient, login_url='/patient/login/')
def patient_change_password_complete(request, patient_id):
  patient = patient_does_not_exists(patient_id)

  change_password_complete = PatientChangePasswordComplete.as_view(
    extra_context={'patient': patient}
  )

  return change_password_complete(request)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient, login_url='/patient/login/')
def patient_dashboard(request, patient_id):
  patient = patient_does_not_exists(patient_id)

  context = {
    'patient': patient,
  }

  return render(request, 'patient_dashboard.html', context)

##########################################
############ Helper Functions ############
##########################################

def patient_does_not_exists(patient_id):
  """
  Redirects to login/dashboard if patient_id is invalid
  """
  try:
    return Patient.objects.get(id=patient_id)
  except Patient.DoesNotExist:
    redirect('patient_login')