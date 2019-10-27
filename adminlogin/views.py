from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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

from adminlogin.forms import UserEditForm, UserQrForm

from core.models import User, Admin
from userlogs.models import Logs
from adminlogin.anonymise import anonymise_and_store

import hashlib
import qrcode

class AdminLogin(LoginView):
  """
  Custom admin login view that extends from Django's LoginView
  """
  form_class = AuthenticationForm
  template_name = 'admin_login.html'

  def form_valid(self, form):
    """
    Checks if a user is an admin
    """
    try:
      admin = form.get_user().admin_username
    except Admin.DoesNotExist:
      admin = None

    if admin is not None:
      auth_login(self.request, form.get_user())
      nonce = get_random_string(length=16, allowed_chars=u'abcdefghijklmnopqrstuvwxyz0123456789')
      user = admin.username
      # if len(user.device_id_hash) > 0 and len(user.android_id_hash) > 0:
      user.sub_id_hash = nonce  # change field
      user.save()  # this will update only
      Logs.objects.create(type='LOGIN', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='Admin Login')
      return redirect('admin_qr', admin_id=admin.id)
      # else:
      #   return redirect('admin_token_register', admin_id=admin.id)
    else:
      form = AuthenticationForm

      context = {
        'form': form,
      }

      return render(self.request, 'admin_login.html', context)

class AdminLogout(LogoutView):
  """
  Custom admin logout view that extends from Django's LogoutView
  """
  next_page = '/'

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_settings(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Settings] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username

  # the action has not gone through QR verification
  if len(user.sub_id_hash) > 0:
    return redirect('admin_login')

  Logs.objects.create(type='READ', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='Settings')

  context = {
    'admin': admin,
    'user': user,
  }

  return render(request, 'admin_settings.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_edit_settings(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='UPDATE', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Edit Settings] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username

  # the action has not gone through QR verification
  if len(user.sub_id_hash) > 0:
    return redirect('admin_login')

  form = UserEditForm(request.POST or None, instance=user)

  if request.method == 'POST':
    if form.is_valid():
      user.save()
      Logs.objects.create(type='UPDATE', user_id=user.id, interface='ADMIN', status=STATUS_OK, details='Edit Settings')
      return redirect('admin_settings', admin_id=admin_id)
    else:
      Logs.objects.create(type='UPDATE', user_id=user.id, interface='ADMIN', status=STATUS_ERROR, details='[Edit Settings] Invalid Form')
      context = {
        'form': form,
        'admin': admin,
        'user': user,
      }
      return render(request, 'admin_edit_settings.html', context)

    Logs.objects.create(type='READ', user_id=user.id, interface='ADMIN', status=STATUS_OK, details='[Edit Settings] Render Settings Form')

  context = {
    'form': form,
    'admin': admin,
    'user': user,
  }

  return render(request, 'admin_edit_settings.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_qr(request, admin_id):
  # the session will expire 15 minutes after inactivity, and will require log in again.
  request.session.set_expiry(900)

  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username

  # when user purposefully try to traverse to this url but they haven't registered
  # if len(user.device_id_hash) == 0 and len(user.android_id_hash) == 0:
  #   return redirect("admin_token_register", admin_id=admin.id)

  if len(user.sub_id_hash) > 0:
    nonce = user.sub_id_hash
  else:
    # if somehow bypassed login
    return redirect('admin_login')

  form = UserQrForm(request.POST or None)

  if form.is_valid():
    cd = form.cleaned_data
    otp = cd.get('otp')
    if otp == '1234':
    # if user.device_id_hash == recovered_value(user.android_id_hash, nonce, otp):
      # give HttpResponse only or render page you need to load on success
      # delete the nonce
      user.sub_id_hash = ""
      user.save()
      return redirect('admin_dashboard', admin_id=admin.id)
    else:
      # if fails, then redirect to custom url/page
      return redirect('admin_login')

  else:
    context = {
      'form': UserQrForm(),
      'nonce': nonce,
    }
    return render(request, "admin_qr.html", context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_dashboard(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Dashboard] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username

  # the action has not gone through QR verification
  if len(user.sub_id_hash) > 0:
    return redirect('admin_login')

  Logs.objects.create(type='READ', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='Dashboard')

  context = {
    'admin': admin,
  }

  return render(request, 'admin_dashboard.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def show_all_logs(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show All Logs] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  logs_list = Logs.objects.all().order_by('-timestamp')

  paginator = Paginator(logs_list, 10)
  page = request.GET.get('page', 1)
  try:
    logs = paginator.page(page)
  except PageNotAnInteger:
    logs = paginator.page(1)
  except EmptyPage:
    logs = paginator.page(paginator.num_pages)

  context = {
    'admin': admin,
    'logs': logs,
  }

  Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='[Show All Logs] Page: ' + str(page))

  return render(request, 'show_all_logs.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def anonymise_records(request, admin_id):
  # Checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Anonymise Records] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username

  context = {
    'admin': admin
  }

  # Check if GET (first load) or POST (subsequent load)
  if request.method == 'POST':
    # Pre-Process DB
    anonymise_and_store()
    Logs.objects.create(type='UPDATE', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='Anonymise Records')

    return render(request, 'anonymise_records.html', context)

  # GET - First load
  else:
    return render(request, 'anonymise_records.html', context)

##########################################
############ Helper Functions ############
##########################################

STATUS_OK = 1
STATUS_ERROR = 0

def admin_does_not_exists(admin_id):
  """
  Redirects to login if admin_id is invalid
  """
  try:
    return Admin.objects.get(id=admin_id)
  except Admin.DoesNotExist:
    Logs.objects.create(type='READ', user_id=admin_id, interface='ADMIN', status=STATUS_ERROR, details='Admin ID is invalid.')
    redirect('admin_login')