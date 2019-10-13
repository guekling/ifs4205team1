from django.shortcuts import render, redirect
from django.template import RequestContext
from django.urls import reverse_lazy

from django.utils.crypto import get_random_string

from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

from patientlogin.forms import UserEditForm, UserQrForm

from core.models import User, Patient
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, ReadingsPerm, TimeSeriesPerm, DocumentsPerm, ImagesPerm, VideosPerm

import hashlib
import qrcode

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
      patient = form.get_user().patient_username
    except Patient.DoesNotExist:
      patient = None

    if patient is not None:
      auth_login(self.request, form.get_user())
      nonce = get_random_string(length=16, allowed_chars=u'abcdefghijklmnopqrstuvwxyz0123456789')
      user = patient.username
      user.sub_id_hash = nonce  # change field
      user.save()  # this will update only
      return redirect('patient_qr', patient_id=patient.id)
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
    url = reverse_lazy('patient_change_password_complete', kwargs={'patient_id': user.patient.id})
    return url

class PatientChangePasswordComplete(PasswordChangeDoneView):
  """
  Custom patient change password complete view that extends from Django's PasswordChangeDoneView
  """
  template_name = 'patient_change_password_complete.html'

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def patient_settings(request, patient_id):
  patient = patient_does_not_exists(patient_id)
  user = patient.username

  context = {
    'patient': patient,
    'user': user,
  }

  return render(request, 'patient_settings.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
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
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def patient_change_password(request, patient_id):
  patient = patient_does_not_exists(patient_id)

  change_password = PatientChangePassword.as_view(
    extra_context={'patient': patient}
  )

  return change_password(request)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def patient_change_password_complete(request, patient_id):
  patient = patient_does_not_exists(patient_id)

  change_password_complete = PatientChangePasswordComplete.as_view(
    extra_context={'patient': patient}
  )

  return change_password_complete(request)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def patient_qr(request, patient_id):
  patient = patient_does_not_exists(patient_id)
  user = patient.username
  if len(user.sub_id_hash) > 0:
    nonce = user.sub_id_hash
  else:
    return redirect('patient_login')

  form = UserQrForm(request.POST or None)

  if form.is_valid():
    cd = form.cleaned_data
    otp = cd.get('otp')
    if user.device_id_hash == recovered_value(user.android_id_hash, nonce, otp):
      # give HttpResponse only or render page you need to load on success
      user.sub_id_hash = ""
      user.save()
      return redirect('patient_dashboard', patient_id=patient.id)
    else:
      # if fails, then redirect to custom url/page
      return redirect('patient_login')

  else:
    context = {
      'form': UserQrForm(),
      'nonce': nonce,
    }
    return render(request, "patient_qr.html", context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
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
  Redirects to login if patient_id is invalid
  """
  try:
    return Patient.objects.get(id=patient_id)
  except Patient.DoesNotExist:
    redirect('patient_login')

def recovered_value(hash_id, nonce, otp):
  x = hashlib.sha256((hash_id + nonce).encode()).hexdigest()
  xor = '{:x}'.format(int(x[-6:], 16) ^ int(otp, 16))

  return hashlib.sha256((xor).encode()).hexdigest()

def make_qr(nonce):
  qr = qrcode.QRCode(
    version=1,
    box_size=15,
    border=5
  )

  qr.add_data(nonce)
  qr.make(fit=True)
  img = qr.make_image(fill='black', back_color='white')

  return img
