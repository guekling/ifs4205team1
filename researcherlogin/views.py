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

from core.models import Researcher, User, Locked
from researcherlogin.forms import UserEditForm, UserQrForm
from userlogs.models import Logs


class ResearcherLogin(LoginView):
  """
  Custom researcher login view that extends from Django's LoginView
  """
  form_class = AuthenticationForm
  template_name = 'researcher_login.html'

  def form_valid(self, form):
    """
    Checks if user is a researcher
    """
    try:
      researcher = form.get_user().researcher_username
    except Researcher.DoesNotExist:
      researcher = None

    if researcher is not None:
      auth_login(self.request, form.get_user())
      nonce = get_random_string(length=16, allowed_chars=u'abcdefghijklmnopqrstuvwxyz0123456789')
      user = researcher.username
      if len(user.hashed_last_six) > 0 and len(user.hashed_id) > 0:
        user.latest_nonce = nonce # change field
        user.nonce_timestamp = datetime.now()
        user.save() # this will update only
        Logs.objects.create(type='LOGIN', user_id=user.uid, interface='RESEARCHER', status=STATUS_OK, details='Researcher Login')
        return redirect('researcher_qr', researcher_id=researcher.id)
      else:
        return redirect('researcher_token_register', researcher_id=researcher.id)
    else:
      form = AuthenticationForm

      context = {
        'form': form
      }

      return render(self.request, 'researcher_login.html', context)

@receiver(user_login_failed)
def user_logged_in_failed(sender, credentials, request, **kwargs):
  # Checks if user is a valid user
  try:
    user= User.objects.filter(username=credentials['username'])
    user = user[0]
    user.loginattempts = user.loginattempts + 1
    user.save()
    Logs.objects.create(type='LOGIN', interface='RESEARCHER', status=STATUS_ERROR, details='[LOGIN] User(' + credentials['username'] + ') Failed Login. Failed Attempt ' + str(user.loginattempts))
  except IndexError:
    Logs.objects.create(type='LOGIN', interface='RESEARCHER', status=STATUS_ERROR, details='[LOGIN] User(' + credentials['username'] + ') Not Found')

  # Checks if login attempts more than 3
  if user.pass_login_attempts() == False:
    user.locked = True
    user.save()
    ipaddr = visitor_ip_address(request)
    Locked.objects.create(lockedipaddr=ipaddr, lockeduser=user) # save the locked user's ip address
    Logs.objects.create(type='LOGIN', interface='RESEARCHER', status=STATUS_ERROR, details='[LOGIN] User(' + credentials['username'] + ') is locked out.')

@receiver(user_logged_in)
def user_logged_in_success(sender, user, request, **kwargs):
  if user.loginattempts > 0:
    user.loginattempts = 0 # reset failed login attempts
    user.save()

class ResearcherLogout(LogoutView):
  """
  Custom researcher logout view that extends from Django's LogoutView
  """
  next_page = '/researcher/login'

class ResearcherChangePassword(PasswordChangeView):
  """
  Custom researcher change password view that extends from Django's PasswordChangeView
  """
  form_class = PasswordChangeForm
  template_name = 'researcher_change_password.html'

  def get_success_url(self):
    user = self.request.user
    url = reverse_lazy('researcher_change_password_complete', kwargs={'researcher_id': user.researcher.id})
    return url

class ResearcherChangePasswordComplete(PasswordChangeDoneView):
  """
  Custom researcher change password complete view that extends from Django's PasswordChangeDoneView
  """
  template_name = 'researcher_change_password_complete.html'

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/researcher/login/')
def researcher_settings(request, researcher_id):
  # Checks if logged in researcher has the same id as in the URL
  if (request.user.researcher_username.id != researcher_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[Settings] Logged in user does not match ID in URL. URL ID: ' + str(researcher_id))
    return redirect('researcher_login')

  researcher = researcher_does_not_exists(researcher_id)
  user = researcher.username

  Logs.objects.create(type='READ', user_id=user.uid, interface='RESEARCHER', status=STATUS_OK, details='Settings')

  context = {
    'researcher': researcher,
    'user': user
  }

  return render(request, 'researcher_settings.html', context)

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/researcher/login/')
def researcher_edit_settings(request, researcher_id):
  # Checks if logged in researcher has the same id as in the URL
  if (request.user.researcher_username.id != researcher_id):
    Logs.objects.create(type='UPDATE', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[Edit Settings] Logged in user does not match ID in URL. URL ID: ' + str(researcher_id))
    return redirect('researcher_login')

  researcher = researcher_does_not_exists(researcher_id)
  user = researcher.username

  form = UserEditForm(request.POST or None, instance=user)

  if request.method == 'POST':
    if form.is_valid():
      user.save()
      Logs.objects.create(type='UPDATE', user_id=user.uid, interface='RESEARCHER', status=STATUS_OK, details='Edit Settings')
      return redirect('researcher_settings', researcher_id=researcher_id)
    else:
      Logs.objects.create(type='UPDATE', user_id=user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[Edit Settings] Invalid Form')
      context = {
        'form': form,
        'researcher': researcher,
        'user': user
      }
      return render(request, 'researcher_edit_settings.html', context)

  Logs.objects.create(type='READ', user_id=user.uid, interface='RESEARCHER', status=STATUS_OK, details='[Edit Settings] Render Settings Form')

  context = {
    'form': form,
    'researcher': researcher,
    'user': user
  }

  return render(request, 'researcher_edit_settings.html', context)

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/researcher/login/')
def researcher_change_password(request, researcher_id):
  # Checks if logged in researcher has the same id as in the URL
  if (request.user.researcher_username.id != researcher_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[Change PW] Logged in user does not match ID in URL. URL ID: ' + str(researcher_id))
    return redirect('researcher_login')

  researcher = researcher_does_not_exists(researcher_id)
  user = researcher.username

  change_password = ResearcherChangePassword.as_view(
    extra_context={'researcher': researcher}
  )

  Logs.objects.create(type='UPDATE', user_id=user.uid, interface='RESEARCHER', status=STATUS_OK, details='Change Password')

  return change_password(request)

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/researcher/login/')
def researcher_change_password_complete(request, researcher_id):
  # Checks if logged in researcher has the same id as in the URL
  if (request.user.researcher_username.id != researcher_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[Change PW Complete] Logged in user does not match ID in URL. URL ID: ' + str(researcher_id))
    return redirect('researcher_login')

  researcher = researcher_does_not_exists(researcher_id)
  user = researcher.username

  change_password_complete = ResearcherChangePasswordComplete.as_view(
      extra_context={'researcher': researcher}
    )

  return change_password_complete(request)

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_not_locked(), login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
@ratelimit(key='ip', rate='100/m')
def researcher_qr(request, researcher_id):
  # the session will expire 15 minutes after inactivity, and will require log in again
  request.session.set_expiry(900)

  # ipaddr = visitor_ip_address(request)

  # Checks if IP address is on list of locked IP addressesi
  # for locked in Locked.objects.all():
  #   if locked.lockedipaddr == ipaddr:
  #     Logs.objects.create(type='LOGIN', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[2FA] User(' + str(request.user.uid) + ') of IP Address ' + str(ipaddr) + ' is using a locked IP address.')
  #     request.session.flush()

  # Checks if logged in researcher has the same id as in the URL
  if (request.user.researcher_username.id != researcher_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[2FA] Logged in user does not match ID in URL. URL ID: ' + str(researcher_id))
    return redirect('researcher_login')

  researcher = researcher_does_not_exists(researcher_id)
  user = researcher.username

  # when user purposefully try to traverse to this url but they haven't registered
  if len(user.hashed_last_six) == 0 and len(user.hashed_id) == 0:
    Logs.objects.create(type='LOGIN', user_id=user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[2FA] URL traversal. Not Registered yet.')
    return redirect("researcher_token_register")

  # require a valid nonce (exists and not expired). a nonce expires after 3 minutes
  if len(user.latest_nonce) > 0 and (datetime.now(timezone.utc) - user.nonce_timestamp).total_seconds() <= 180:
    nonce = user.latest_nonce
  else:
    # if somehow bypassed login
    Logs.objects.create(type='LOGIN', user_id=user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[2FA] Username-password login bypassed. No valid nonce.')
    return redirect('researcher_login')

  form = UserQrForm(request.POST or None)

  if form.is_valid():
    cd = form.cleaned_data
    otp = cd.get('otp')
    # timeout, nonce expires
    if (datetime.now(timezone.utc) - user.nonce_timestamp).total_seconds() > 180:
      return redirect('patient_login')
    if user.hashed_last_six == recovered_value(user.hashed_id, nonce, otp):
      # given HttpResponse only or render page you need to load on success
      user.latest_nonce = ""
      user.save()
      Logs.objects.create(type='LOGIN', user_id=user.uid, interface='RESEARCHER', status=STATUS_OK, details='[2FA] Login successful. Nonce deleted.')
      return redirect('researcher_dashboard', researcher_id=researcher.id)
    else:
      # if fails, then redirect to custom url/page
      Logs.objects.create(type='LOGIN', user_id=user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[2FA] Wrong OTP.')
      return redirect('researcher_login')

  else:
    context = {
      'form': UserQrForm(),
      'nonce': nonce
    }

    return render(request, 'researcher_qr.html', context)

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_not_locked(), login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
def researcher_token_register(request, researcher_id):
  # the session will expire 15 minutes after inactivity, and will require log in again
  request.session.set_expiry(900)

  # ipaddr = visitor_ip_address(request)

  # Checks if IP address is on list of locked IP addressesi
  # for locked in Locked.objects.all():
  #   if locked.lockedipaddr == ipaddr:
  #     Logs.objects.create(type='LOGIN', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[2FA Reminder] User(' + str(request.user.uid) + ') of IP Address ' + str(ipaddr) + ' is using a locked IP address.')
  #     request.session.flush()

  # Checks if logged in researcher has the same id as in the URL
  if (request.user.researcher_username.id != researcher_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[2FA Reminder] Logged in user does not match ID in URL. URL ID: ' + str(researcher_id))
    return redirect('researcher_login')

  researcher = researcher_does_not_exists(researcher_id)
  user = researcher.username

  # device already linked
  if len(user.hashed_last_six) > 0 and len(user.hashed_id) > 0:
    Logs.objects.create(type='LOGIN', user_id=user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[2FA_Reminder] URL traversal. Already registered.')
    return redirect("repeat_register", user_id=user.uid)

  return render(request, "researcher_token_register.html")

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/researcher/login/')
def researcher_dashboard(request, researcher_id):
  # Checks if logged in researcher has the same id as in the URL
  if (request.user.researcher_username.id != researcher_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[Dashboard] Logged in user does not match ID in URL. URL ID: ' + str(researcher_id))
    return redirect('researcher_login')

  researcher = researcher_does_not_exists(researcher_id)
  user = researcher.username

  Logs.objects.create(type='READ', user_id=user.uid, interface='RESEARCHER', status=STATUS_OK, details='Dashboard')

  context = {
    'researcher': researcher
  }

  return render(request, 'researcher_dashboard.html', context)

##########################################
############ Helper Functions ############
##########################################

STATUS_OK = 1
STATUS_ERROR = 0

def researcher_does_not_exists(researcher_id):
  """
  Redirects to login if researcher_id is invalid
  """
  try:
    return Researcher.objects.get(id=researcher_id)
  except Researcher.DoesNotExist:
    redirect('researcher_login')

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