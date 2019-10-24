from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from core.models import Patient, Healthcare
from patientrecords.models import Documents, DocumentsPerm
from userlogs.models import Logs

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

  notes = Documents.objects.filter(patient_id=patient, type="Healthcare Professional Note")

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

  context = {
    'patient': patient,
    'note': note,
  }

  Logs.objects.create(type='READ', user_id=patient.username.uid, interface='PATIENT', status=STATUS_OK, details='Show Note ' + str(note_id))

  return render(request, 'show_note.html', context)

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
    Logs.objects.create(type='READ', user_id=patient_id, interface='PATIENT', status=STATUS_ERROR, details='Patient ID is invalid.')
    redirect('patient_login')