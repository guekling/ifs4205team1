import hashlib
from datetime import datetime, timezone

import qrcode
from django.contrib.auth import (
  login as auth_login
)
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string

from adminlogin.anonymise import anonymise_and_store
from adminlogin.forms import UserEditForm, UserQrForm, EditRecordTypesPermForm
from core.models import Admin, Researcher
from userlogs.models import Logs


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
      if len(user.hashed_last_six) > 0 and len(user.hashed_id) > 0:
        user.latest_nonce = nonce  # change field
        user.nonce_timestamp = datetime.now()
        user.save()  # this will update only
        Logs.objects.create(type='LOGIN', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='Admin Login')
        return redirect('admin_qr', admin_id=admin.id)
      else:
        return redirect('admin_token_register', admin_id=admin.id)
    else:
      form = AuthenticationForm

      context = {
        'form': form,
      }

      return render(self.request, 'admin_login.html', context)

@receiver(user_login_failed)
def user_logged_in_failed(sender, credentials, request, **kwargs):
  # Checks if user is a valid user
  try:
    user= User.objects.filter(username=credentials['username'])
    user = user[0]
    user.loginattempts = user.loginattempts + 1
    user.save()
    Logs.objects.create(type='LOGIN', interface='ADMIN', status=STATUS_ERROR, details='[LOGIN] User(' + credentials['username'] + ') Failed Login. Failed Attempt ' + str(user.loginattempts))
  except IndexError:
    Logs.objects.create(type='LOGIN', interface='ADMIN', status=STATUS_ERROR, details='[LOGIN] User(' + credentials['username'] + ') Not Found')

  # Checks if login attempts more than 3
  if user.pass_login_attempts() == False:
    user.locked = True
    user.save()
    ipaddr = visitor_ip_address(request)
    Locked.objects.create(lockedipaddr=ipaddr, lockeduser=user) # save the locked user's ip address
    Logs.objects.create(type='LOGIN', interface='ADMIN', status=STATUS_ERROR, details='[LOGIN] User(' + credentials['username'] + ') is locked out.')

@receiver(user_logged_in)
def user_logged_in_success(sender, user, request, **kwargs):
  if user.loginattempts > 0:
    user.loginattempts = 0 # reset failed login attempts
    user.save()

class AdminLogout(LogoutView):
  """
  Custom admin logout view that extends from Django's LogoutView
  """
  next_page = '/'

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/')
def admin_settings(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Settings] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username

  Logs.objects.create(type='READ', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='Settings')

  context = {
    'admin': admin,
    'user': user,
  }

  return render(request, 'admin_settings.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/')
def admin_edit_settings(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='UPDATE', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Edit Settings] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username

  form = UserEditForm(request.POST or None, instance=user)

  if request.method == 'POST':
    if form.is_valid():
      user.save()
      Logs.objects.create(type='UPDATE', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='Edit Settings')
      return redirect('admin_settings', admin_id=admin_id)
    else:
      Logs.objects.create(type='UPDATE', user_id=user.id, interface='ADMIN', status=STATUS_ERROR, details='[Edit Settings] Invalid Form')
      context = {
        'form': form,
        'admin': admin,
        'user': user,
      }
      return render(request, 'admin_edit_settings.html', context)

  Logs.objects.create(type='READ', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='[Edit Settings] Render Settings Form')

  context = {
    'form': form,
    'admin': admin,
    'user': user,
  }

  return render(request, 'admin_edit_settings.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_not_locked(), login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_qr(request, admin_id):
  # the session will expire 15 minutes after inactivity, and will require log in again.
  request.session.set_expiry(900)

  ipaddr = visitor_ip_address(request)

  # Checks if IP address is on list of locked IP addressesi
  for locked in Locked.objects.all():
    if locked.lockedipaddr == ipaddr:
      Logs.objects.create(type='LOGIN', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[2FA] User(' + str(request.user.uid) + ') of IP Address ' + str(ipaddr) + ' is using a locked IP address.')
      request.session.flush()

  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username

  # when user purposefully try to traverse to this url but they haven't registered
  if len(user.hashed_last_six) == 0 and len(user.hashed_id) == 0:
    return redirect("admin_token_register", admin_id=admin.id)

  # require a valid nonce (exists and not expired). a nonce expires after 3 minutes
  if len(user.latest_nonce) > 0 and (datetime.now(timezone.utc) - user.nonce_timestamp).total_seconds() <= 180:
    nonce = user.latest_nonce
  else:
    # if somehow bypassed login
    return redirect('admin_login')

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
@user_passes_test(lambda u: u.is_not_locked(), login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_token_register(request, admin_id):
  # the session will expire 15 minutes after inactivity, and will require log in again.
  request.session.set_expiry(900)

  ipaddr = visitor_ip_address(request)

  # Checks if IP address is on list of locked IP addressesi
  for locked in Locked.objects.all():
    if locked.lockedipaddr == ipaddr:
      Logs.objects.create(type='LOGIN', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[LOGIN] User(' + str(request.user.uid) + ') of IP Address ' + str(ipaddr) + ' is using a locked IP address.')
      request.session.flush()

  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Dashboard] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username

  # device already linked
  if len(user.hashed_last_six) > 0 and len(user.hashed_id) > 0:
    Logs.objects.create(type='ADMIN', user_id=user.uid, interface='ADMIN', status=STATUS_ERROR, details='[2FA_Reminder] URL traversal. Already registered.')
    return redirect("repeat_register", user_id=user.uid)

  return render(request, "admin_token_register.html")

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/')
def admin_dashboard(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Dashboard] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username

  Logs.objects.create(type='READ', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='Dashboard')

  context = {
    'admin': admin,
  }

  return render(request, 'admin_dashboard.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/')
def show_all_logs(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show All Logs] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username
  
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
@user_passes_test(lambda u: u.pass_2fa(), login_url='/')
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

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/')
def show_all_researchers(request, admin_id):
  # Checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show All Reseachers] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username

  # UNDONE: ADD in logic
  researchers = Researcher.objects.all().order_by('username')

  Logs.objects.create(type='READ', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='Show All Researchers')

  context = {
    'admin': admin,
    'researchers': researchers
  }

  return render(request, 'show_all_researchers.html', context)


@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/')
def edit_recordtypes_perm(request, admin_id, researcher_id):
  # Checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Edit Researcher Record Types Permission] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  user = admin.username
  researcher = check_researcher_exists(researcher_id)

  recordtypes_choices = get_recordtypes_choices()
  recordtypes_perm = get_recordtypes_perm(researcher)
  form = EditRecordTypesPermForm(recordtypes_choices=recordtypes_choices, recordtypes_perm=recordtypes_perm)

  if request.method == 'POST':
    form = EditRecordTypesPermForm(request.POST, recordtypes_choices=recordtypes_choices, recordtypes_perm=recordtypes_perm)
    if form.is_valid():
      recordtypes_selected = form.cleaned_data['recordtypesperm']

      if isinstance(recordtypes_selected, list):
        store_updated_perm(researcher, recordtypes_selected)
        Logs.objects.create(type='UPDATE', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='Edit Researcher Record Types Permission')
        context = {
          'admin': admin
        }
        return redirect('show_all_researchers', admin_id=admin_id)
      else:
        Logs.objects.create(type='UPDATE', user_id=user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Edit Researcher Record Types Permission] Invalid record types selected')
        form.add_error('recordtypesperm', 'Invalid record types selected')
        context = {
          'form': form,
          'admin': admin,
          'researcher': researcher
        }
        return render(request, 'edit_recordtypes_perm.html', context)

    else:
      Logs.objects.create(type='UPDATE', user_id=user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Edit Researcher Record Types Permission] Invalid form')
      form.add_error(None, 'Invalid form')
      context = {
        'form': form,
        'admin': admin,
        'researcher': researcher
      }
      return render(request, 'edit_recordtypes_perm.html', context)
  else:
    context = {
      'form': form,
      'admin': admin,
      'researcher': researcher
    }
    return render(request, 'edit_recordtypes_perm.html', context)


##########################################
############ Helper Functions ############
##########################################

STATUS_OK = 1
STATUS_ERROR = 0

DIAGNOSIS_NAME = 'diagnosis'
BP_READING_NAME = 'bp_reading'
HR_READING_NAME = 'hr_reading'
TEMP_READING_NAME = 'temp_reading'
CANCER_IMG_NAME = 'cancer_img'
MRI_IMG_NAME = 'mri_img'
ULTRASOUND_IMG_NAME = 'ultrasound_img'
XRAY_IMG_NAME = 'xray_img'
GASTROSCOPE_VID_NAME = 'gastroscope_vid'
GAIT_VID_NAME = 'gait_vid'

RECORD_TYPES_NAME_LIST = [
  DIAGNOSIS_NAME,
  BP_READING_NAME,
  HR_READING_NAME,
  TEMP_READING_NAME,
  CANCER_IMG_NAME,
  MRI_IMG_NAME,
  ULTRASOUND_IMG_NAME,
  XRAY_IMG_NAME,
  GASTROSCOPE_VID_NAME,
  GAIT_VID_NAME
]

DIAGNOSIS_DISPLAY_NAME = 'Diagnosis'
BP_READING_DISPLAY_NAME = 'Blood Pressure (BP) Readings'
HR_READING_DISPLAY_NAME = 'Heart Rate (HR) Readings'
TEMP_READING_DISPLAY_NAME = 'Temperature (TEMP) Readings'
CANCER_IMG_DISPLAY_NAME = 'Cancer Images'
MRI_IMG_DISPLAY_NAME = 'MRI Images'
ULTRASOUND_IMG_DISPLAY_NAME = 'Ultrasound Images'
XRAY_IMG_DISPLAY_NAME = 'Xray Images'
GASTROSCOPE_VID_DISPLAY_NAME = 'Gastroscope Videos'
GAIT_VID_DISPLAY_NAME = 'Gait Videos'

def recovered_value(hash_id, nonce, otp):
  x = hashlib.sha256((hash_id + nonce).encode()).hexdigest()
  xor = '{:x}'.format(int(x[-6:], 16) ^ int(otp, 16))

  return hashlib.sha256((xor).encode()).hexdigest()

def get_recordtypes_choices():
  recordtypes_choices = []

  recordtypes_choices.append((DIAGNOSIS_NAME, DIAGNOSIS_DISPLAY_NAME))
  recordtypes_choices.append((BP_READING_NAME, BP_READING_DISPLAY_NAME))
  recordtypes_choices.append((HR_READING_NAME, HR_READING_DISPLAY_NAME))
  recordtypes_choices.append((TEMP_READING_NAME, TEMP_READING_DISPLAY_NAME))
  recordtypes_choices.append((CANCER_IMG_NAME, CANCER_IMG_DISPLAY_NAME))
  recordtypes_choices.append((MRI_IMG_NAME, MRI_IMG_DISPLAY_NAME))
  recordtypes_choices.append((ULTRASOUND_IMG_NAME, ULTRASOUND_IMG_DISPLAY_NAME))
  recordtypes_choices.append((XRAY_IMG_NAME, XRAY_IMG_DISPLAY_NAME))
  recordtypes_choices.append((GASTROSCOPE_VID_NAME, GASTROSCOPE_VID_DISPLAY_NAME))
  recordtypes_choices.append((GAIT_VID_NAME, GAIT_VID_DISPLAY_NAME))

  return recordtypes_choices

def get_recordtypes_perm(researcher):
  recordtypes_perm = []

  # Add record type to checkbox choices only if perm returns True
  if (researcher.get_diagnosis_perm()):
    recordtypes_perm.append(DIAGNOSIS_NAME)

  if (researcher.get_bp_reading_perm()):
    recordtypes_perm.append(BP_READING_NAME)

  if (researcher.get_hr_reading_perm()):
    recordtypes_perm.append(HR_READING_NAME)

  if (researcher.get_temp_reading_perm()):
    recordtypes_perm.append(TEMP_READING_NAME)

  if (researcher.get_cancer_img_perm()):
    recordtypes_perm.append(CANCER_IMG_NAME)

  if (researcher.get_mri_img_perm()):
    recordtypes_perm.append(MRI_IMG_NAME)

  if (researcher.get_ultrasound_img_perm()):
    recordtypes_perm.append(ULTRASOUND_IMG_NAME)

  if (researcher.get_xray_img_perm()):
    recordtypes_perm.append(XRAY_IMG_NAME)

  if (researcher.get_gastroscope_vid_perm()):
    recordtypes_perm.append(GASTROSCOPE_VID_NAME)

  if (researcher.get_gait_vid_perm()):
    recordtypes_perm.append(GAIT_VID_NAME)

  return recordtypes_perm

def store_updated_perm(researcher, recordtypes_selected):
  print("STORE_UPDATED_PERM")
  print(RECORD_TYPES_NAME_LIST)
  print(recordtypes_selected)

  for recordtype in RECORD_TYPES_NAME_LIST:
    if recordtype == DIAGNOSIS_NAME:
      if recordtype in recordtypes_selected:
        researcher.diagnosis = True
      else:
        researcher.diagnosis = False

    if recordtype == BP_READING_NAME:
      if recordtype in recordtypes_selected:
        researcher.bp_reading = True
      else:
        researcher.bp_reading = False

    if recordtype == HR_READING_NAME:
      if recordtype in recordtypes_selected:
        researcher.hr_reading = True
      else:
        researcher.hr_reading = False

    if recordtype == TEMP_READING_NAME:
      if recordtype in recordtypes_selected:
        researcher.temp_reading = True
      else:
        researcher.temp_reading = False

    if recordtype == CANCER_IMG_NAME:
      if recordtype in recordtypes_selected:
        researcher.cancer_img = True
      else:
        researcher.cancer_img = False

    if recordtype == MRI_IMG_NAME:
      if recordtype in recordtypes_selected:
        researcher.mri_img = True
      else:
        researcher.mri_img = False

    if recordtype == ULTRASOUND_IMG_NAME:
      if recordtype in recordtypes_selected:
        researcher.ultrasound_img = True
      else:
        researcher.ultrasound_img = False

    if recordtype == XRAY_IMG_NAME:
      if recordtype in recordtypes_selected:
         researcher.xray_img = True
      else:
        researcher.xray_img = False

    if recordtype == GASTROSCOPE_VID_NAME:
      if recordtype in recordtypes_selected:
        researcher.gastroscope_vid = True
      else:
        researcher.gastroscope_vid = False

    if recordtype == GAIT_VID_NAME:
      if recordtype in recordtypes_selected:
        researcher.gait_vid = True
      else:
        researcher.gait_vid = False

  researcher.save()
  print("DONE")

def admin_does_not_exists(admin_id):
  """
  Redirects to login if admin_id is invalid
  """
  try:
    return Admin.objects.get(id=admin_id)
  except Admin.DoesNotExist:
    Logs.objects.create(type='READ', user_id=admin_id, interface='ADMIN', status=STATUS_ERROR, details='Admin ID is invalid.')
    redirect('admin_login')

def check_researcher_exists(researcher_id):
  """
  Redirects to show_all_researchers if researcher_id is invalid
  """
  try:
    return Researcher.objects.get(id=researcher_id)
  except Researcher.DoesNotExist:
    redirect('show_all_researchers')

def visitor_ip_address(request):

  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return ip