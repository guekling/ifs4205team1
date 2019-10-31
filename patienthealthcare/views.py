from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponse

from core.models import User, Patient, Healthcare
from patientrecords.models import Documents, DocumentsPerm
from userlogs.models import Logs

import os
from mimetypes import guess_type

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def show_all_notes(request, patient_id):
  """
  List all healthcare professional notes written about the patient
  """
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='UPDATE', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Show All Notes] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)
  user = User.objects.filter(patient_username=patient) # Returns a Queryset

  # Only show notes that patients are allowed to read
  notes = Documents.objects.filter(documentsperm_documents__username__in=user, documentsperm_documents__perm_value__in=[2,3], patient_id=patient, type="Healthcare Professional Note")

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='Show All Notes')

  context = {
    'patient': patient,
    'notes': notes,
  }

  return render(request, 'show_all_notes.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def show_note(request, patient_id, note_id):
  """
  Show information of a single healthcare professional note
  """
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='UPDATE', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Show Note] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  try:
    note = Documents.objects.filter(id=note_id)
    note = note[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Show Note] Note ID is invalid.')
    return redirect('show_all_notes', patient_id=patient_id)

  # Path to view restricted record
  note_path = os.path.join(settings.PROTECTED_MEDIA_PATH, str(note_id))

  context = {
    'patient': patient,
    'note': note,
    'note_path': note_path,
  }

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='Show Note ' + str(note_id))

  return render(request, 'show_note.html', context)

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def download_note(request, patient_id, note_id):
  """
  Downloads a single healthcare professional note
  """
  if (request.user.patient_username.id != patient_id):
    Logs.objects.create(type='UPDATE', user_id=request.user.uid, interface='PATIENT', status=STATUS_ERROR, details='[Download Note] Logged in user does not match ID in URL. URL ID: ' + str(patient_id))
    return redirect('/patient/login/')

  patient = patient_does_not_exists(patient_id)

  try:
    note = Documents.objects.filter(id=note_id)
    note = note[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Download Note] Note ID is invalid.')
    return redirect('show_all_notes', patient_id=patient_id)

  try:
    file_path = note.data.path
  except ValueError:
    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Download Note] No data path in note ' + str(note_id))
    return redirect('show_note', patient_id=patient_id, note_id=note_id)

  file_path = note.data.path
  file_name = note.data.name.split('/', 1)[1]

  with open(file_path, 'rb') as note:
    content_type = guess_type(file_path)[0]
    response = HttpResponse(note, content_type=content_type)
    response['Content-Length'] = os.path.getsize(file_path)
    response['Content-Disposition'] = "attachment; filename=%s" %  file_name

    Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='[Download Note] Download Note ' + str(note_id))

    return response

##########################################
############ Helper Functions ############
##########################################

STATUS_OK = 1
STATUS_ERROR = 0

def patient_does_not_exists(patient_id): # TODO: This function is never called?
  """
  Redirects to login/dashboard if patient_id is invalid
  """
  try:
    return Patient.objects.get(id=patient_id)
  except Patient.DoesNotExist:
    Logs.objects.create(type='READ', user_id=patient_id, interface='PATIENT', status=STATUS_ERROR, details='[PatientHealthcare] Patient ID is invalid.')
    redirect('patient_login')