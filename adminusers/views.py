from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required, user_passes_test

from adminusers.forms import CreateNewPatient, CreateNewHealthcare

from core.models import User, Admin, Patient, Healthcare, Researcher
from userlogs.models import Logs

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_show_all_users(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show All Users] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  users_list = User.objects.all().order_by('-date_joined')

  paginator = Paginator(users_list, 10)
  page = request.GET.get('page', 1)
  try:
    users = paginator.page(page)
  except PageNotAnInteger:
    users = paginator.page(1)
  except EmptyPage:
    users = paginator.page(paginator.num_pages)

  context = {
    'admin': admin,
    'users': users,
  }

  Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='[Show All Users] Page: ' + str(page))

  return render(request, 'admin_show_all_users.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_show_user(request, admin_id, user_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show User] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)

  try:
    user = User.objects.filter(uid=user_id)
    user = user[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show User] User ID is invalid.')
    return redirect('admin_show_all_users', admin_id=admin_id)

  context = {
    'admin': admin,
    'user': user,
  }

  Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='[Show User] Page: ' + str(user_id))

  return render(request, 'admin_show_user.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_show_all_patients(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show All Patients] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  patients_list = Patient.objects.all()

  paginator = Paginator(patients_list, 10)
  page = request.GET.get('page', 1)
  try:
    patients = paginator.page(page)
  except PageNotAnInteger:
    patients = paginator.page(1)
  except EmptyPage:
    patients = paginator.page(paginator.num_pages)

  context = {
    'admin': admin,
    'patients': patients,
  }

  Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='[Show All Patients] Page: ' + str(page))

  return render(request, 'admin_show_all_patients.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_show_patient(request, admin_id, patient_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show Patient] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)

  try:
    patient = Patient.objects.filter(id=patient_id)
    patient = patient[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show Patient] Patient ID is invalid.')
    return redirect('admin_show_all_patients', admin_id=admin_id)

  context = {
    'admin': admin,
    'patient': patient,
  }

  Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='[Show Patient] Page: ' + str(patient_id))

  return render(request, 'admin_show_patient.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_new_patient(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[New Patient] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)

  form = CreateNewPatient(request.POST or None)

  if request.method == 'POST':
    if form.is_valid():
      user = form.save(commit=False)
      gender = form.cleaned_data['gender']
      user.gender = gender
      user.save()

      patient = Patient.objects.create(username=user)

      Logs.objects.create(type='UPDATE', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='New Patient')
      return redirect('admin_show_patient', admin_id=admin_id, patient_id=patient.id)
    else:
      Logs.objects.create(type='UPDATE', user_id=admin.username.uid, interface='ADMIN', status=STATUS_ERROR, details='[New Patient] Invalid Form')
      context = {
        'form': form,
        'admin': admin,
      }
      return render(request, 'admin_new_patient.html', context)

  Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='[New Patient] Render Form')

  context = {
    'form': form,
    'admin': admin,
  }

  return render(request, 'admin_new_patient.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_show_all_healthcare(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show All Healthcare] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  healthcare_list = Healthcare.objects.all()

  paginator = Paginator(healthcare_list, 10)
  page = request.GET.get('page', 1)
  try:
    healthcare = paginator.page(page)
  except PageNotAnInteger:
    healthcare = paginator.page(1)
  except EmptyPage:
    healthcare = paginator.page(paginator.num_pages)

  context = {
    'admin': admin,
    'healthcare': healthcare,
  }

  Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='[Show All Healthcare] Page: ' + str(page))

  return render(request, 'admin_show_all_healthcare.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_show_healthcare(request, admin_id, healthcare_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show Healthcare] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)

  try:
    healthcare = Healthcare.objects.filter(id=healthcare_id)
    healthcare = healthcare[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show Healthcare] Healthcare ID is invalid.')
    return redirect('admin_show_all_healthcare', admin_id=admin_id)

  context = {
    'admin': admin,
    'healthcare': healthcare,
  }

  Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='[Show Healthcare] Page: ' + str(healthcare_id))

  return render(request, 'admin_show_healthcare.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_new_healthcare(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[New Healthcare] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)

  form = CreateNewHealthcare(request.POST or None)

  if request.method == 'POST':
    if form.is_valid():
      user = form.save(commit=False)
      gender = form.cleaned_data['gender']
      user.gender = gender
      user.save()

      license = form.cleaned_data['license']
      patients = form.cleaned_data['patients']

      healthcare = Healthcare.objects.create(username=user, license=license)
      for patient in patients:
        healthcare.patients.add(patient)

      Logs.objects.create(type='UPDATE', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='New Healthcare')
      return redirect('admin_show_healthcare', admin_id=admin_id, healthcare_id=healthcare.id)
    else:
      Logs.objects.create(type='UPDATE', user_id=admin.username.uid, interface='ADMIN', status=STATUS_ERROR, details='[New Healthcare] Invalid Form')
      context = {
        'form': form,
        'admin': admin,
      }
      return render(request, 'admin_new_healthcare.html', context)

  Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='[New Healthcare] Render Form')

  context = {
    'form': form,
    'admin': admin,
  }

  return render(request, 'admin_new_healthcare.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_show_all_researchers(request, admin_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show All Researchers] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)
  researchers_list = Researcher.objects.all()

  paginator = Paginator(researchers_list, 10)
  page = request.GET.get('page', 1)
  try:
    researchers = paginator.page(page)
  except PageNotAnInteger:
    researchers = paginator.page(1)
  except EmptyPage:
    researchers = paginator.page(paginator.num_pages)

  context = {
    'admin': admin,
    'researchers': researchers,
  }

  Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='[Show All Researchers] Page: ' + str(page))

  return render(request, 'admin_show_all_researchers.html', context)

@login_required(login_url='/')
@user_passes_test(lambda u: u.is_admin(), login_url='/')
def admin_show_researcher(request, admin_id, researcher_id):
  # checks if logged in admin has the same id as in the URL
  if (request.user.admin_username.id != admin_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show Researcher] Logged in user does not match ID in URL. URL ID: ' + str(admin_id))
    return redirect('/')

  admin = admin_does_not_exists(admin_id)

  try:
    researcher = Researcher.objects.filter(id=researcher_id)
    researcher = researcher[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_ERROR, details='[Show Researcher] Researcher ID is invalid.')
    return redirect('admin_show_all_researchers', admin_id=admin_id)

  context = {
    'admin': admin,
    'researcher': researcher,
  }

  Logs.objects.create(type='READ', user_id=admin.username.uid, interface='ADMIN', status=STATUS_OK, details='[Show Researcher] Page: ' + str(researcher_id))

  return render(request, 'admin_show_researcher.html', context)

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