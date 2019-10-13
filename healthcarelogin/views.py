from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.utils.crypto import get_random_string

from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

from patientlogin.forms import UserEditForm, UserQrForm

from core.models import User, Healthcare

import hashlib
import qrcode

class HealthcareLogin(LoginView):
  """
  Custom healthcare professional login view that extends from Django's LoginView
  """
  form_class = AuthenticationForm
  template_name = 'healthcare_login.html'

  def form_valid(self, form):
    """
    Checks if a user is a healthcare professional
    """
    try:
      healthcare = form.get_user().healthcare_username
    except Healthcare.DoesNotExist:
      healthcare = None

    if healthcare is not None:
      auth_login(self.request, form.get_user())
      nonce = get_random_string(length=16, allowed_chars=u'abcdefghijklmnopqrstuvwxyz0123456789')
      user = healthcare.username
      user.sub_id_hash = nonce  # change field
      user.save()  # this will update only
      return redirect('healthcare_qr', healthcare_id=healthcare.id)
    else:
      form = AuthenticationForm

      context = {
        'form': form,
      }

      return render(self.request, 'healthcare_login.html', context)

class HealthcareLogout(LogoutView):
  """
  Custom healthcare logout view that extends from Django's LogoutView
  """
  next_page = '/healthcare/login'

class HealthcareChangePassword(PasswordChangeView):
  """
  Custom healthcare change password view that extends from Django's PasswordChangeView
  """
  form_class = PasswordChangeForm
  template_name = 'healthcare_change_password.html'

  def get_success_url(self):
    user = self.request.user
    url = reverse_lazy('healthcare_change_password_complete', kwargs={'healthcare_id': user.healthcare.id})
    return url

class HealthcareChangePasswordComplete(PasswordChangeDoneView):
  """
  Custom healthcare change password complete view that extends from Django's PasswordChangeDoneView
  """
  template_name = 'healthcare_change_password_complete.html'

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def healthcare_settings(request, healthcare_id):
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)
  user = healthcare.username

  context = {
    'healthcare': healthcare,
    'user': user,
  }

  return render(request, 'healthcare_settings.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def healthcare_edit_settings(request, healthcare_id):
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)
  user = healthcare.username
  form = UserEditForm(request.POST or None, instance=user)

  if request.method == 'POST':
    if form.is_valid():
      user.save()
      return redirect('healthcare_settings', healthcare_id=healthcare_id)
    else:
      context = {
        'form': form,
        'healthcare': healthcare,
        'user': user,
      }
      return render(request, 'healthcare_edit_settings.html', context)

  context = {
    'form': form,
    'healthcare': healthcare,
    'user': user,
  }

  return render(request, 'healthcare_edit_settings.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def healthcare_change_password(request, healthcare_id):
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  change_password = HealthcareChangePassword.as_view(
    extra_context={'healthcare': healthcare}
  )

  return change_password(request)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def healthcare_change_password_complete(request, healthcare_id):
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  change_password_complete = HealthcareChangePasswordComplete.as_view(
    extra_context={'healthcare': healthcare}
  )

  return change_password_complete(request)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def healthcare_qr(request, healthcare_id):
  healthcare = healthcare_does_not_exists(healthcare_id)
  user = healthcare.username
  if len(user.sub_id_hash) > 0:
    nonce = user.sub_id_hash
  else:
    return redirect('healthcare_login')

  form = UserQrForm(request.POST or None)

  if form.is_valid():
    cd = form.cleaned_data
    otp = cd.get('otp')
    if user.device_id_hash == recovered_value(user.android_id_hash, nonce, otp):
      # give HttpResponse only or render page you need to load on success
      user.sub_id_hash = ""
      user.save()
      return redirect('healthcare_dashboard', healthcare_id=healthcare.id)
    else:
      # if fails, then redirect to custom url/page
      return redirect('healthcare_login')

  else:
    context = {
      'form': UserQrForm(),
      'nonce': nonce,
    }
    return render(request, "healthcare_qr.html", context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def healthcare_dashboard(request, healthcare_id):
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  context = {
    'healthcare': healthcare,
  }

  return render(request, 'healthcare_dashboard.html', context)

##########################################
############ Helper Functions ############
##########################################

def healthcare_does_not_exists(healthcare_id):
  """
  Redirects to login if healthcare_id is invalid
  """
  try:
    return Healthcare.objects.get(id=healthcare_id)
  except Healthcare.DoesNotExist:
    redirect('healthcare_login')

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
