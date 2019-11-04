import hashlib
from datetime import datetime, timezone

import qrcode
from django.contrib.auth import (
  login as auth_login
)
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from ratelimit.decorators import ratelimit

from core.models import User, Patient, Locked
from patientlogin.forms import UserEditForm, UserQrForm
from patientrecords.models import Notifications
from userlogs.models import Logs


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
      if len(user.hashed_last_six) > 0 and len(user.hashed_id) > 0:
        user.latest_nonce = nonce  # change field
        user.nonce_timestamp = datetime.now()
        user.save()  # this will update only
        Logs.objects.create(type='LOGIN', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='[LOGIN] User(' + str(user.uid) + ') Patient Login')
        return redirect('patient_qr', patient_id=patient.id)
      else:
        return redirect('patient_token_register', patient_id=patient.id)
    else:
      form = AuthenticationForm

      context = {
        'form': form,
      }

      return render(self.request, 'patient_login.html', context)

@receiver(user_login_failed)
def user_logged_in_failed(sender, credentials, request, **kwargs):
  # Checks if user is a valid user
  try:
    user= User.objects.filter(username=credentials['username'])
    user = user[0]
    user.loginattempts = user.loginattempts + 1
    user.save()
    Logs.objects.create(type='LOGIN', interface='PATIENT', status=STATUS_ERROR, details='[LOGIN] User(' + credentials['username'] + ') Failed Login. Failed Attempt ' + str(user.loginattempts))

    # Checks if login attempts more than 3
    if user.pass_login_attempts() == False:
      user.locked = True
      user.save()
      ipaddr = visitor_ip_address(request)
      Locked.objects.create(lockedipaddr=ipaddr, lockeduser=user) # save the locked user's ip address
      Logs.objects.create(type='LOGIN', interface='PATIENT', status=STATUS_ERROR, details='[LOGIN] User(' + credentials['username'] + ') is locked out.')
  except IndexError:
    Logs.objects.create(type='LOGIN', interface='PATIENT', status=STATUS_ERROR, details='[LOGIN] User(' + credentials['username'] + ') Not Found')

@receiver(user_logged_in)
def user_logged_in_success(sender, user, request, **kwargs):
  if user.loginattempts > 0:
    user.loginattempts = 0 # reset failed login attempts
    user.save()

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
    url = reverse_lazy('patient_change_password_complete', kwargs={'patient_id':user.patient_username.id})
    return url

class PatientChangePasswordComplete(PasswordChangeDoneView):
  """
  Custom patient change password complete view that extends from Django's PasswordChangeDoneView
  """
  template_name = 'patient_change_password_complete.html'

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/patient/login/')
def patient_notifications(request, patient_id):
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Settings] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  Logs.objects.create(type='READ', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='Notifications')

  noti_list = Notifications.objects.filter(patient=patient).order_by('-timestamp', 'from_user')

  context = {
    'patient': patient,
    'user': user,
    'noti_list': noti_list,
  }

  for notif in noti_list:
    if notif.status < 3:
      notif.status += 1
      notif.save()

  return render(request, 'patient_notifications.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/patient/login/')
def patient_login_history(request, patient_id):
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Settings] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  Logs.objects.create(type='READ', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='Login History')

  context = {
    'patient': patient,
    'user': user,
  }

  return render(request, 'patient_login_history.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/patient/login/')
def patient_settings(request, patient_id):
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Settings] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  Logs.objects.create(type='READ', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='Settings')

  context = {
    'patient': patient,
    'user': user,
  }

  return render(request, 'patient_settings.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/patient/login/')
def patient_edit_settings(request, patient_id):
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='UPDATE', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Edit Settings] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

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
@user_passes_test(lambda u: u.pass_2fa(), login_url='/patient/login/')
def patient_change_password(request, patient_id):
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Change PW] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  change_password = PatientChangePassword.as_view(
    extra_context={'patient': patient}
  )

  Logs.objects.create(type='UPDATE', user_id=user.uid, interface='PATIENT', status=STATUS_OK, details='Change Password')

  return change_password(request)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/patient/login/')
def patient_change_password_complete(request, patient_id):
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Change PW Complete] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  change_password_complete = PatientChangePasswordComplete.as_view(
    extra_context={'patient': patient}
  )

  return change_password_complete(request)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_not_locked(), login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
@ratelimit(key='ip', rate='100/m')
def patient_qr(request, patient_id):
  # the session will expire 15 minutes after inactivity, and will require log in again.
  request.session.set_expiry(900)

  # ipaddr = visitor_ip_address(request)

  # Checks if IP address is on list of locked IP addressesi
  # for locked in Locked.objects.all():
  #   if locked.lockedipaddr == ipaddr:
  #     Logs.objects.create(type='LOGIN', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[PATIENT_QR] User(' + str(request.user.uid) + ') of IP Address ' + str(ipaddr) + ' is using a locked IP address.')
  #     request.session.flush()

  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[2FA] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

  # when user purposefully try to traverse to this url but they haven't registered
  if len(user.hashed_last_six) == 0 and len(user.hashed_id) == 0:
    Logs.objects.create(type='LOGIN', user_id=user.uid, interface='PATIENT', status=STATUS_ERROR, details='[2FA] URL traversal. Not Registered yet.')
    return redirect("patient_token_register", patient_id=patient.id)

  # require a valid nonce (exists and not expired). a nonce expires after 3 minutes
  if len(user.latest_nonce) > 0 and (datetime.now(timezone.utc) - user.nonce_timestamp).total_seconds() <= 180:
    nonce = user.latest_nonce
  else:
    # if somehow bypassed login
    Logs.objects.create(type='LOGIN', user_id=user.uid, interface='PATIENT', status=STATUS_ERROR, details='[2FA] Username-password login bypassed. No valid nonce.')
    return redirect('patient_login')

  form = UserQrForm(request.POST or None)

  if form.is_valid():
    cd = form.cleaned_data
    otp = cd.get('otp')
    # timeout, nonce expires
    if (datetime.now(timezone.utc) - user.nonce_timestamp).total_seconds() > 180:
      return redirect('patient_login')
    if user.hashed_last_six == recovered_value(user.hashed_id, nonce, otp):
      # give HttpResponse only or render page you need to load on success
      # delete the nonce
      user.latest_nonce = ""
      user.login6 = user.login5
      user.login5 = user.login4
      user.login4 = user.login3
      user.login3 = user.login2
      user.login2 = user.login1
      user.login1 = datetime.now()
      user.ip6 = user.ip5
      user.ip5 = user.ip4
      user.ip4 = user.ip3
      user.ip3 = user.ip2
      user.ip2 = user.ip1
      user.ip1 = visitor_ip_address(request)
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
@user_passes_test(lambda u: u.is_not_locked(), login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def patient_token_register(request, patient_id):
  # the session will expire 15 minutes after inactivity, and will require log in again.
  request.session.set_expiry(900)

  # ipaddr = visitor_ip_address(request)

  # Checks if IP address is on list of locked IP addressesi
  # for locked in Locked.objects.all():
  #   if locked.lockedipaddr == ipaddr:
  #     Logs.objects.create(type='LOGIN', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[2FA Reminder] User(' + str(request.user.uid) + ') of IP Address ' + str(ipaddr) + ' is using a locked IP address.')
  #     request.session.flush()

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
@user_passes_test(lambda u: u.pass_2fa(), login_url='/patient/login/')
def patient_dashboard(request, patient_id):
  # checks if logged in patient has the same id as in the URL
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Dashboard] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = patient.username

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

def patient_does_not_exists(patient_id):
  """
  Redirects to login if patient_id is invalid
  """
  try:
    return Patient.objects.get(id=patient_id)
  except Patient.DoesNotExist:
    Logs.objects.create(type='READ', user_id=patient_id, interface='PATIENT', status=STATUS_ERROR, details='[PatientLogin] Patient ID is invalid. Patient ID: ' + str(patient_id))
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

def visitor_ip_address(request):

  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return ip

