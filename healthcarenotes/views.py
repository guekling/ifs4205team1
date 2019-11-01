from __future__ import division, unicode_literals

import codecs
import os
from mimetypes import guess_type

import bleach
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, redirect

from core.models import Healthcare
from healthcarenotes.forms import DocumentsPermissionEditForm, AddHealthcareNote, AddHealthcareNoteForPatient, \
  EditHealthcareNote
from patientrecords.models import Documents, DocumentsPerm
from userlogs.models import Logs


@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/healthcare/login/')
def show_all_healthcare_notes(request, healthcare_id):
  """
  List all healthcare notes the healthcare professional has written for his patients
  """ 
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show All Notes] Logged in user does not match ID in URL. URL ID: ' + str(healthcare_id))
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  notes = Documents.objects.filter(owner_id_id=healthcare.username, type='Healthcare Professional Note')

  Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Show All Notes]')

  context = {
    'healthcare': healthcare,
    'notes': notes,
  }

  return render(request, 'show_all_healthcare_notes.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/healthcare/login/')
def show_healthcare_note(request, healthcare_id, note_id):
  """
  Show information of a single healthcare professional note
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show Note] Logged in user does not match ID in URL. URL ID: ' + str(healthcare_id))
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    note = Documents.objects.filter(id=note_id)
    note = note[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show Note] Note ID is invalid. Invalid ID: ' + str(note_id))
    return redirect('show_all_healthcare_notes', healthcare_id=healthcare_id)

  # Path to view restricted record
  note_path = os.path.join(settings.PROTECTED_MEDIA_PATH, str(note_id))

  permissions = DocumentsPerm.objects.filter(docs_id=note_id)

  Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Show Note] Show Note ' + str(note_id))

  context = {
    'healthcare': healthcare,
    'note': note,
    'permissions': permissions,
    'note_path': note_path,
  }

  return render(request, 'show_healthcare_note.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/healthcare/login/')
def download_healthcare_note(request, healthcare_id, note_id):
  """
  Downloads a single healthcare professional note
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Download Note] Logged in user does not match ID in URL. URL ID: ' + str(healthcare_id))
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    note = Documents.objects.filter(id=note_id)
    note = note[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Download Note] Note ID is invalid. Invalid ID: ' + str(note_id))
    return redirect('show_all_healthcare_notes', healthcare_id=healthcare_id)

  try:
    file_path = note.data.path
  except ValueError:
    Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='PATIENT', status=STATUS_ERROR, details='[Download Notes] No data path in note ' + str(note_id))
    return redirect('show_healthcare_note', healthcare_id=healthcare_id, note_id=note_id)

  file_path = note.data.path # E.g. /home/sadm/Desktop/.../x.html
  file_name = note.data.name.split('/', 1)[1] # x.html

  with open(file_path, 'rb') as note:
    content_type = guess_type(file_path)[0]
    response = HttpResponse(note, content_type=content_type)
    response['Content-Length'] = os.path.getsize(file_path)
    response['Content-Disposition'] = "attachment; filename=%s" %  file_name

    Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Download Note] Download Note ' + str(note_id))

    return response

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/healthcare/login/')
def edit_healthcare_note_permission(request, healthcare_id, note_id, perm_id):
  """
  Edit a permission of a single healthcare_professional_note
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Edit Note Permission] Logged in user does not match ID in URL. URL ID: ' + str(healthcare_id))
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    note = Documents.objects.filter(id=note_id)
    note = note[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Edit Note Permission] Note ID is invalid. Invalid ID: ' + str(note_id))
    return redirect('show_all_healthcare_notes', healthcare_id=healthcare_id)

  try:
    permission = DocumentsPerm.objects.filter(id = perm_id)
    permission = permission[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Edit Note Permission] Permission ID is invalid.')
    return redirect('show_healthcare_note', healthcare_id=healthcare_id, note_id=note_id)

  form = DocumentsPermissionEditForm(request.POST or None, instance=permission)

  if request.method == 'POST':
    if form.is_valid():
      permission.save()
      Logs.objects.create(type='UPDATE', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Edit Note Permission] Edit Note ' + str(note_id) + ' permission ' + str(perm_id))
      return redirect('show_healthcare_note', healthcare_id=healthcare_id, note_id=note_id)
    else:
      Logs.objects.create(type='UPDATE', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Edit Note Permission] Invalid Form')
      context = {
        'form': form,
        'healthcare': healthcare,
        'note': note,
        'permission': permission
      }
      return render(request, 'edit_healthcare_note_permission.html', context)

  Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Edit Note Permission] Render Form for Note ' + str(note.id))

  context = {
    'form': form,
    'healthcare': healthcare,
    'note': note,
    'permission': permission
  }

  return render(request, 'edit_healthcare_note_permission.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/healthcare/login/')
def create_healthcare_note(request, healthcare_id):
  """
  Create a new healthcare professional note
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Create Note] Logged in user does not match ID in URL. URL ID: ' + str(healthcare_id))
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  form = AddHealthcareNote(request.POST, healthcare=healthcare)

  if request.method == 'POST':
    if form.is_valid():
      note_patient = form.cleaned_data['patient']
      Logs.objects.create(type='UPDATE', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Create Note] Create new healthcare note')
      return redirect('create_healthcare_note_for_patient', healthcare_id=healthcare_id, patient_id=note_patient.id)
    else:
      Logs.objects.create(type='UPDATE', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Create Note] Invalid Form')
      context = {
        'form': form,
        'healthcare': healthcare,
      }
      return render(request, 'create_healthcare_note.html', context)

  Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Create Note] Render Form')

  context = {
    'form': form,
    'healthcare': healthcare,
  }

  return render(request, 'create_healthcare_note.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/healthcare/login/')
def create_healthcare_note_for_patient(request, healthcare_id, patient_id):
  """
  Create a new healthcare professional note for a single patient
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Show Note for Patient] Logged in user does not match ID in URL. URL ID: ' + str(healthcare_id))
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    patient = healthcare.patients.all().filter(id=patient_id)
    patient = patient[0]
  except IndexError:
    Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Create Note for Patient] Patient ID is invalid.')
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

      # Save new note into database
      note = Documents.objects.create(title=title, type="Healthcare Professional Note", owner_id=healthcare.username, patient_id=patient)

      # Put attachments for note
      new_note = new_note + "<p>Attachments:</p>"
      new_note = new_note + "<p>Readings:</p>"

      for reading in attach_readings:
        datetime = reading.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        url = settings.HOSTED_SITE_URL + "/protectedrecord/" + str(reading.id)
        new_note = new_note + "<p><a href=" + url + ">" + datetime + " " + reading.type + "</a></p>"
        note.attach_readings.add(reading)

      new_note = new_note + "<p>TimeSeries:</p>"
      for timeseries in attach_timeseries:
        datetime = timeseries.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        url = settings.HOSTED_SITE_URL + "/protectedrecord/" + str(timeseries.id)
        new_note = new_note + "<p><a href=" + url + ">" + datetime + "</a></p>"
        note.attach_timeseries.add(timeseries)

      new_note = new_note + "<p>Images:</p>"
      for image in attach_images:
        datetime = image.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        url = settings.HOSTED_SITE_URL + "/protectedrecord/" + str(image.id)
        new_note = new_note + "<p><a href=" + url + ">" + datetime + " Type: " + image.type + " Title: " + image.title + "</a></p>"
        note.attach_images.add(image)

      new_note = new_note + "<p>Videos:</p>"
      for video in attach_videos:
        datetime = video.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        url = settings.HOSTED_SITE_URL + "/protectedrecord/" + str(video.id)
        new_note = new_note + "<p><a href=" + url + ">" + datetime + " Type: " + video.type + " Title: " + video.title + "</a></p>"
        note.attach_videos.add(video)

      base_dir = settings.BASE_DIR
      note_path = os.path.join(base_dir, 'media', 'documents', title + ".html") # directory to save new note in
      data_path = os.path.join("documents", title + ".html") # directory to save into data value

      # Create HTML file for new note
      save_note = open(note_path,"w")
      save_note.write(new_note)
      save_note.close()

      # Add data into new note
      note_title = title + ".html"
      note.data = "{}{}".format("documents/", note_title)
      note.save()

      # Set default permissions for note
      permission = DocumentsPerm.objects.create(docs_id=note, given_by=healthcare.username, perm_value=3)
      permission.username.add(patient.username)
      permissions = DocumentsPerm.objects.filter(docs_id=note) # List all permissions of the note

      Logs.objects.create(type='UPDATE', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Create Note for Patient] Create new note for patient.')

      return redirect('show_healthcare_note', healthcare_id=healthcare.id, note_id=note.id)
    else:
      Logs.objects.create(type='UPDATE', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Create Note] Invalid Form')
      context = {
        'form': form,
        'healthcare': healthcare,
        'patient': patient,
      }
      return render(request, 'create_healthcare_note_for_patient.html', context)

  Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Create Note for Patient] Render Form')

  context = {
    'form': form,
    'healthcare': healthcare,
    'patient': patient,
  }

  return render(request, 'create_healthcare_note_for_patient.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare(), login_url='/healthcare/login/')
@user_passes_test(lambda u: u.pass_2fa(), login_url='/healthcare/login/')
def edit_healthcare_note(request, healthcare_id, note_id):
  """
  Edit healthcare professional note for a single patient
  """
  # checks if logged in healthcare professional has the same id as in the URL
  if (request.user.healthcare_username.id != healthcare_id):
    Logs.objects.create(type='READ', user_id=request.user.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Edit Note] Logged in user does not match ID in URL. URL ID: ' + str(healthcare_id))
    return redirect('/healthcare/login/')

  healthcare = healthcare_does_not_exists(healthcare_id)

  try:
    note = Documents.objects.filter(id=note_id)
    note = note[0]
    Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Edit Note] Note ID is invalid.')
  except IndexError:
    return redirect('show_all_healthcare_notes', healthcare_id=healthcare_id)

  patient = note.patient_id

  note_full_path = note.data.path # Eg. /home/sadm/Desktop/.../x.html
  note_project_path = note.data.name # Eg. documents/x.html

  try: 
    open_note = codecs.open(note_full_path, 'r', 'utf-8') # open note 
  except FileNotFoundError:
    Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Edit Note] File not found.')
    return redirect('show_healthcare_note', healthcare_id=healthcare.id, note_id=note.id)

  open_note = codecs.open(note_full_path, 'r', 'utf-8') # open note
  document = BeautifulSoup(open_note.read(), 'html.parser').get_text() # read note
  split_at = 'Attachments:'
  split = document.split(split_at, 1) # split the note to remove attachments

  form = EditHealthcareNote(request.POST, patient=patient, initial={
    'title': note.title, 
    'note': split[0],
  })

  saved_attached_readings = note.attach_readings.all()
  saved_attached_timeseries = note.attach_timeseries.all()
  saved_attached_videos = note.attach_videos.all()
  saved_attached_images = note.attach_images.all()
  
  if request.method == 'POST':
    if form.is_valid():
      title = bleach.clean(form.cleaned_data['title'], tags=[], attributes=[], protocols=[], strip=True)
      edit_note = bleach.clean(form.cleaned_data['note'], attributes=[], protocols=[], strip=True)
      attach_readings = form.cleaned_data['attach_readings']
      attach_timeseries = form.cleaned_data['attach_timeseries']
      attach_images = form.cleaned_data['attach_images']
      attach_videos = form.cleaned_data['attach_videos']

      # Put new attachments for note
      edit_note = edit_note + "<p>Attachments:</p>"
      edit_note = edit_note + "<p>Readings:</p>"

      # Clear previous saved attachments in database
      note.attach_readings.clear()
      note.attach_images.clear()
      note.attach_timeseries.clear()
      note.attach_videos.clear()

      for reading in attach_readings:
        datetime = reading.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        url = settings.HOSTED_SITE_URL + "/protectedrecord/" + str(reading.id)
        edit_note = edit_note + "<p><a href=" + url + ">" + datetime + " " + reading.type + "</a></p>"
        note.attach_readings.add(reading) # Saved attachment to database

      edit_note = edit_note + "<p>TimeSeries:</p>"
      for timeseries in attach_timeseries:
        datetime = timeseries.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        url = settings.HOSTED_SITE_URL + "/protectedrecord/" + str(timeseries.id)
        edit_note = edit_note + "<p><a href=" + url + ">" + datetime + "</a></p>"
        note.attach_timeseries.add(timeseries) # Saved attachment to database

      edit_note = edit_note + "<p>Images:</p>"
      for image in attach_images:
        datetime = image.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        url = settings.HOSTED_SITE_URL + "/protectedrecord/" + str(image.id)
        edit_note = edit_note + "<p><a href=" + url + ">" + datetime + " Type: " + image.type + " Title: " + image.title + "</a></p>"
        note.attach_images.add(image) # Saved attachment to database

      edit_note = edit_note + "<p>Videos:</p>"
      for video in attach_videos:
        datetime = video.timestamp.strftime("%a, %d %b %Y %I:%M %p")
        url = settings.HOSTED_SITE_URL + "/protectedrecord/" + str(video.id)
        edit_note = edit_note + "<p><a href=" + url + ">" + datetime + " Type: " + video.type + " Title: " + video.title + "</a></p>"
        note.attach_videos.add(video) # Saved attachment to database

      note_path = note.data.path

      # Create HTML file for edited note
      save_note = open(note_path,"w")
      save_note.write(edit_note)
      save_note.close()

      # Add data into edited note
      new_note_title = title + ".html"
      note.data = "{}{}".format("documents/", new_note_title)

      # Update note title
      note.title = title
      note.save()

      Logs.objects.create(type='UPDATE', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Edit Note] Edit Note ' + str(note_id) + ' for patient ' + str(patient.id))

      return redirect('show_healthcare_note', healthcare_id=healthcare.id, note_id=note.id)
    else:
      Logs.objects.create(type='UPDATE', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_ERROR, details='[Edit Note] Invalid Form')
      context = {
        'form': form,
        'healthcare': healthcare,
        'patient': patient,
        'note': note,
        'saved_attached_readings': saved_attached_readings,
        'saved_attached_timeseries': saved_attached_timeseries,
        'saved_attached_videos': saved_attached_videos,
        'saved_attached_images': saved_attached_images,
      }
      return render(request, 'edit_healthcare_note.html', context)

  Logs.objects.create(type='READ', user_id=healthcare.username.uid, interface='HEALTHCARE', status=STATUS_OK, details='[Edit Note] Render Form')

  context = {
    'form': form,
    'healthcare': healthcare,
    'patient': patient,
    'note': note,
    'saved_attached_readings': saved_attached_readings,
    'saved_attached_timeseries': saved_attached_timeseries,
    'saved_attached_videos': saved_attached_videos,
    'saved_attached_images': saved_attached_images,
  }

  return render(request, 'edit_healthcare_note.html', context)

##########################################
############ Helper Functions ############
##########################################

STATUS_OK = 1
STATUS_ERROR = 0

def healthcare_does_not_exists(healthcare_id):
  """
  Redirects to login if healthcare_id is invalid
  """
  try:
    return Healthcare.objects.get(id=healthcare_id)
  except Healthcare.DoesNotExist:
    Logs.objects.create(type='READ', user_id=healthcare_id, interface='HEALTHCARE', status=STATUS_ERROR, details='[HealthcareNotes] Healthcare ID is invalid ' + str(healthcare_id))
    redirect('healthcare_login')
