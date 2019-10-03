from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from core.models import Patient, Healthcare
from patientrecords.models import Documents, DocumentsPerm

@login_required(login_url='/patient/login/')
@user_passes_test(lambda u: u.is_patient(), login_url='/patient/login/')
def show_all_notes(request, patient_id):
  """
  List all healthcare professional notes written about the patient
  """
  patient = patient_does_not_exists(patient_id)

  notes = Documents.objects.filter(patient_id=patient, type="Healthcare Professional Note")

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
  patient = patient_does_not_exists(patient_id)

  try:
    note = Documents.objects.filter(id=note_id)
    note = note[0]
  except IndexError:
    return redirect('show_all_notes', patient_id=patient_id)

  context = {
    'patient': patient,
    'note': note,
  }

  return render(request, 'show_note.html', context)

##########################################
############ Helper Functions ############
##########################################

def patient_does_not_exists(patient_id):
  """
  Redirects to login/dashboard if patient_id is invalid
  """
  try:
    return Patient.objects.get(id=patient_id)
  except Patient.DoesNotExist:
    redirect('patient_login')