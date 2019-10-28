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
from userlogs.models import Logs

import hashlib
import qrcode
import datetime

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
      # if len(user.hashed_last_six) > 0 and len(user.hashed_id) > 0:
      user.latest_nonce = nonce  # change field
      user.nonce_timestamp = datetime.datetime.now()
      user.save()  # this will update only
      Logs.objects.create(type='LOGIN', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='Patient Login')
      return redirect('patient_qr', patient_id=patient.id)
      # else:
      #   return redirect('patient_token_register', patient_id=patient.id)
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
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Settings] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  # the action has not gone through QR verification
  if len(user.latest_nonce) > 0:
    return redirect('patient_login')

  Logs.objects.create(type='READ', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='Settings')

  context = {
    'patient': patient,
    'user': user,
  }

  return render(request, 'patient_settings.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def patient_edit_settings(request, patient_id):
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='UPDATE', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Edit Settings] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  # the action has not gone through QR verification
  if len(user.latest_nonce) > 0:
    return redirect('patient_login')

  form = UserEditForm(request.POST or None, instance=user)

  if request.method == 'POST':
    if form.is_valid():
      user.save()
      Logs.objects.create(type='UPDATE', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='Edit Settings')
      return redirect('patient_settings', patient_id=patient_id)
    else:
      Logs.objects.create(type='UPDATE', user_id=user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Edit Settings] Invalid Form')
      context = {
        'form': form,
        'patient': patient,
        'user': user,
      }
      return render(request, 'patient_edit_settings.html', context)

  Logs.objects.create(type='READ', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='[Edit Settings] Render Settings Form')

  context = {
    'form': form,
    'patient': patient,
    'user': user,
  }

  return render(request, 'patient_edit_settings.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def patient_change_password(request, patient_id):
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Change PW] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  # the action has not gone through QR verification
  if len(user.latest_nonce) > 0:
    return redirect('patient_login')

  change_password = PatientChangePassword.as_view(
    extra_context={'patient': patient}
  )

  Logs.objects.create(type='UPDATE', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='Change Password')

  return change_password(request)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def patient_change_password_complete(request, patient_id):
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Change PW Complete] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  # the action has not gone through QR verification
  if len(user.latest_nonce) > 0:
    return redirect('patient_login')

  change_password_complete = PatientChangePasswordComplete.as_view(
    extra_context={'patient': patient}
  )

  return change_password_complete(request)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def patient_qr(request, patient_id):
  # the session will expire 15 minutes after inactivity, and will require log in again.
  request.session.set_expiry(900)

  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[2FA] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  # when user purposefully try to traverse to this url but they haven't registered
  # if len(user.hashed_last_six) == 0 and len(user.hashed_id) == 0:
  #   Logs.objects.create(type='LOGIN', user_id=user.uid, interface='PATIENT', status=STATUS_ERROR, details='[2FA] URL traversal. Not Registered yet.')
  #   return redirect("patient_token_register", patient_id=patient.id)

  # require a valid nonce (exists and not expired)
  if len(user.latest_nonce) > 0:
    nonce = user.latest_nonce
  else:
    # if somehow bypassed login
    Logs.objects.create(type='LOGIN', user_id=user.uid, interface='PATIENT', status=STATUS_ERROR, details='[2FA] Username-password login bypassed. No valid nonce.')
    return redirect('patient_login')

  form = UserQrForm(request.POST or None)

  if form.is_valid():
    cd = form.cleaned_data
    otp = cd.get('otp')
    if otp == '1234':
    # if user.hashed_last_six == recovered_value(user.hashed_id, nonce, otp):
      # give HttpResponse only or render page you need to load on success
      # delete the nonce
      user.latest_nonce = ""
      user.save()
      Logs.objects.create(type='LOGIN', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='[2FA] Login successful. Nonce deleted.')
      return redirect('patient_dashboard', patient_id=patient.id)
    else:
      # if fails, then redirect to custom url/page
      Logs.objects.create(type='LOGIN', user_id=user.uid, interface='PATIENT', status=STATUS_ERROR, details='[2FA] Wrong OTP.')
      return redirect('patient_login')

  else:
    context = {
      'form': UserQrForm(),
      'nonce': nonce,
    }
    return render(request, "patient_qr.html", context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def patient_token_register(request, patient_id):
  # the session will expire 15 minutes after inactivity, and will require log in again.
  request.session.set_expiry(900)

  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[2FA Reminder] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  # device already linked
  if len(user.hashed_last_six) > 0 and len(user.hashed_id) > 0:
    Logs.objects.create(type='LOGIN', user_id=user.uid, interface='PATIENT', status=STATUS_ERROR, details='[2FA_Reminder] URL traversal. Already registered.')
    return redirect("repeat_register", user_id=user.uid)

  return render(request, "patient_token_register.html")

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def patient_dashboard(request, patient_id):
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Dashboard] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  # the action has not gone through QR verification
  if len(user.latest_nonce) > 0:
    return redirect('patient_login')

  Logs.objects.create(type='READ', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='Dashboard')

  context = {
    'patient': patient,
  }

  return render(request, 'patient_dashboard.html', context)

##########################################
############ Helper Functions ############
##########################################

STATUS_OK = 1
STATUS_ERROR = 0

def patient_does_not_exists(patient_id): # TODO: This function is never called?
  """
  Redirects to login if patient_id is invalid
  """
  try:
    return Patient.objects.get(id=patient_id)
  except Patient.DoesNotExist:
    Logs.objects.create(type='READ', user_id=patient_id, interface='PATIENT', status=STATUS_ERROR, details='Patient ID is invalid.')
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
