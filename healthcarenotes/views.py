from __future__ import division, unicode_literals 

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from healthcarenotes.forms import DocumentsPermissionEditForm, AddHealthcareNote, AddHealthcareNoteForPatient, EditHealthcareNote

from core.models import Healthcare
from patientrecords.models import Readings, Images, TimeSeries, Videos, Documents, DocumentsPerm

import bleach
import os
from os.path import join
import codecs
from bs4 import BeautifulSoup

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def show_all_healthcare_notes(request, healthcare_id):
  """
  List all healthcare notes the healthcare professional has written for his patients
  """ 
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  notes = Documents.objects.filter(owner_id_id=healthcare.username)

  context = {
    'healthcare': healthcare,
    'notes': notes,
  }

  return render(request, 'show_all_healthcare_notes.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def show_healthcare_note(request, healthcare_id, note_id):
  """
  Show information of a single healthcare professional note
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    note = Documents.objects.filter(id=note_id)
    note = note[0]
  except IndexError:
    return redirect('show_all_healthcare_notes', healthcare_id=healthcare_id)

  permissions = DocumentsPerm.objects.filter(docs_id=note_id)

  context = {
    'healthcare': healthcare,
    'note': note,
    'permissions': permissions,
  }

  return render(request, 'show_healthcare_note.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def edit_healthcare_note_permission(request, healthcare_id, note_id, perm_id):
  """
  Edit a permission of a single healthcare_professional_note
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    note = Documents.objects.filter(id=note_id)
    note = note[0]
  except IndexError:
    return redirect('show_all_healthcare_notes', healthcare_id=healthcare_id)

  try:
    permission = DocumentsPerm.objects.get(id = perm_id)
  except DocumentsPerm.DoesNotExist:
    redirect('show_healthcare_note.html', healthcare_id=healthcare_id, note_id=note_id)

  form = DocumentsPermissionEditForm(request.POST or None, instance=permission)
  if request.method == 'POST':
    if form.is_valid():
      permission.save()
      return redirect('show_healthcare_note', healthcare_id=healthcare_id, note_id=note_id)
    else:
      context = {
        'form': form,
        'healthcare': healthcare,
        'note': note,
        'permission': permission
      }
      return render(request, 'edit_healthcare_note_permission.html', context)

  context = {
    'form': form,
    'healthcare': healthcare,
    'note': note,
    'permission': permission
  }

  return render(request, 'edit_healthcare_note_permission.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def create_healthcare_note(request, healthcare_id):
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  form = AddHealthcareNote(request.POST, healthcare=healthcare)

  if request.method == 'POST':
    if form.is_valid():
      note_patient = form.cleaned_data['patient']
      return redirect('create_healthcare_note_for_patient', healthcare_id=healthcare_id, patient_id=note_patient.id)
    else:
      context = {
        'form': form,
        'healthcare': healthcare,
      }
      return render(request, 'create_healthcare_note.html', context)

  context = {
    'form': form,
    'healthcare': healthcare,
  }

  return render(request, 'create_healthcare_note.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def create_healthcare_note_for_patient(request, healthcare_id, patient_id):
  """
  Create a new healthcare professional note for a single patient
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    patient = healthcare.patients.all().filter(id=patient_id)
    patient = patient[0]
  except IndexError:
    return redirect('show_all_patients', healthcare_id=healthcare_id)

  form = AddHealthcareNoteForPatient(request.POST, patient=patient)

  if request.method == 'POST':
    if form.is_valid():
      title = bleach.clean(form.cleaned_data['title'], tags=[], attributes=[], protocols=[], strip=True)
      new_note = bleach.clean(form.cleaned_data['note'], attributes=[], protocols=[], strip=True)
      attach_readings = form.cleaned_data['attach_readings']
      attach_timeseries = form.cleaned_data['attach_timeseries']
      attach_images = form.cleaned_data['attach_images']
      attach_videos = form.cleaned_data['attach_videos']

      # Put attachments for note
      new_note = new_note + "<p>Attachments:</p>"
      new_note = new_note + "<p>Readings:</p>"
      for reading in attach_readings:
        datetime = reading.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        new_note = new_note + "<p><a href=\"" + reading.data + "\">" + datetime + " " + reading.type + "</a></p>"

      new_note = new_note + "<p>TimeSeries:</p>"
      for timeseries in attach_timeseries:
        datetime = timeseries.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        new_note = new_note + "<p><a href=\"" + timeseries.data.url + "\">" + datetime + "</a></p>"

      new_note = new_note + "<p>Images:</p>"
      for image in attach_images:
        datetime = image.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        new_note = new_note + "<p><a href=\"" + image.data.url + "\">" + datetime + " Type: " + image.type + " Title: " + image.title + "</a></p>"

      new_note = new_note + "<p>Videos:</p>"
      for video in attach_videos:
        datetime = timeseries.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        new_note = new_note + "<p><a href=\"" + video.data.url + "\">" + datetime + " Type: " + video.type + " Title: " + video.title + "</a></p>"

      base_dir = settings.BASE_DIR
      note_path = os.path.join(base_dir, 'media', 'documents', title + ".html") # directory to save new note in
      data_path = os.path.join("documents", title + ".html") # directory to save into data value

      # Create HTML file for new note
      save_note = open(note_path,"w")
      save_note.write(new_note)
      save_note.close()

      # Save new note into database
      note = Documents.objects.create(title=title, type="Healthcare Professional Note", owner_id=healthcare.username, patient_id=patient, data=data_path)

      # Set default permissions for note
      permission = DocumentsPerm.objects.create(docs_id=note, given_by=healthcare.username, perm_value=2)
      permission.username.add(patient.username)
      permissions = DocumentsPerm.objects.filter(docs_id=note)

      return redirect('show_healthcare_note', healthcare_id=healthcare.id, note_id=note.id)
      
    else:
      context = {
        'form': form,
        'healthcare': healthcare,
        'patient': patient,
        'permissions': permissions,
      }
      return render(request, 'show_healthcare_note.html', context)

  context = {
    'form': form,
    'healthcare': healthcare,
    'patient': patient,
  }

  return render(request, 'create_healthcare_note_for_patient.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
def edit_healthcare_note(request, healthcare_id, note_id):
  """
  Create a new healthcare professional note for a single patient
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    note = Documents.objects.filter(id=note_id)
    note = note[0]
  except IndexError:
    return redirect('show_all_healthcare_notes', healthcare_id=healthcare_id)

  patient = note.patient_id

  base_dir = settings.BASE_DIR
  note_path = os.path.join(base_dir, 'media', 'documents', note.title + ".html")

  open_note = codecs.open(note_path, 'r', 'utf-8') # open note 
  document = BeautifulSoup(open_note.read(), 'html.parser').get_text() # read note
  split_at = 'Attachments:'
  split = document.split(split_at, 1) # split the note to remove attachments

  form = EditHealthcareNote(request.POST, patient=patient, initial={
    'title': note.title, 
    'note': split[0],
  })

  if request.method == 'POST':
    if form.is_valid():
      title = bleach.clean(form.cleaned_data['title'], tags=[], attributes=[], protocols=[], strip=True)
      edit_note = bleach.clean(form.cleaned_data['note'], attributes=[], protocols=[], strip=True)

      edit_note = edit_note + "<p>Attachments:</p>"
      edit_note = edit_note + split[1] # Attachments has not been edited + w/o HTML
      
      save_note = open(note_path,"w")
      save_note.write(edit_note)
      save_note.close()

      note.title = title
      note.save()

      return redirect('show_healthcare_note', healthcare_id=healthcare.id, note_id=note.id)

    else:
      context = {
        'form': form,
        'healthcare': healthcare,
        'patient': patient,
        'note': note,
      }
      return render(request, 'edit_healthcare_note.html', context)

  context = {
    'form': form,
    'healthcare': healthcare,
    'patient': patient,
    'note': note,
  }

  return render(request, 'edit_healthcare_note.html', context)

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

def get_r(record_id):
  readings = Readings.objects.filter(id=record_id)
  timeseries = TimeSeries.objects.filter(id=record_id)
  documents = Documents.objects.filter(id=record_id)
  images = Images.objects.filter(id=record_id)
  videos = Videos.objects.filter(id=record_id)

  return list(chain(readings, timeseries, documents, images, videos))
