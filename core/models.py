import uuid
from datetime import date

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
  username = models.CharField(primary_key=True, max_length=64, unique=True)
  gender = models.CharField(max_length=1) # only allow M/F
  dob = models.DateField()
  age = models.PositiveIntegerField(default=None, blank=True, null=True) # max digits = 3
  address = models.CharField(max_length=150)
  postalcode = models.CharField(max_length=6)
  contactnumber = models.PositiveIntegerField() # max digits = 8
  hashed_id = models.CharField(max_length=64)
  hashed_last_six = models.CharField(max_length=64)
  latest_nonce = models.CharField(max_length=64)
  nonce_timestamp = models.DateTimeField(default=None, blank=True, null=True)
  uid = models.UUIDField(default=uuid.uuid4, editable=False)

  USERNAME_FIELD = 'username'

  def save(self, *args, **kwargs):
    born = self.dob
    today = date.today()
    compute_age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    self.age = compute_age
    return super(User, self).save(*args, **kwargs)

  def is_patient(self):
    """
    Checks if user is a patient.
    """
    try:
      patient = self.patient_username
    except Patient.DoesNotExist:
      patient = None

    if patient is not None:
      return True
    else:
      return False

  def is_healthcare(self):
    """
    Checks if user is a healthcare professional
    """
    try:
      healthcare = self.healthcare_username
    except Healthcare.DoesNotExist:
      healthcare = None

    if healthcare is not None:
      return True
    else:
      return False

  def is_admin(self):
    try:
      admin = self.admin_username
    except Admin.DoesNotExist:
      admin = None

    if admin is not None:
      return True
    else:
      return False

  def is_researcher(self):
    """
    Checks if user is a researcher
    """
    try:
      researcher = self.researcher_username
    except Researcher.DoesNotExist:
      researcher = None

    if researcher is not None:
      return True
    else:
      return False

class Admin(models.Model):
  username = models.OneToOneField( # one admin to one user
    User,
    on_delete=models.CASCADE,
    related_name='admin_username',
    primary_key=True)
  id = models.UUIDField(default=uuid.uuid4, editable=False)

class Patient(models.Model):
  username = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name='patient_username',
    primary_key=True)
  id = models.UUIDField(default=uuid.uuid4, editable=False)

class Healthcare(models.Model):
  username = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name='healthcare_username',
    primary_key=True)
  id = models.UUIDField(default=uuid.uuid4, editable=False)
  license = models.CharField(max_length=16)
  patients = models.ManyToManyField(
    Patient, 
    related_name='healthcare_patients'
  )
  
class Researcher(models.Model):
  username = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name='researcher_username',
    primary_key=True)
  id = models.UUIDField(default=uuid.uuid4, editable=False)
  diagnosis = models.BooleanField(default=False) 
  bp_reading = models.BooleanField(default=False) 
  hr_reading = models.BooleanField(default=False) 
  temp_reading = models.BooleanField(default=False)
  cancer_img = models.BooleanField(default=False) 
  mri_img = models.BooleanField(default=False) 
  ultrasound_img = models.BooleanField(default=False) 
  xray_img = models.BooleanField(default=False)
  gastroscope_vid = models.BooleanField(default=False)
  gait_vid = models.BooleanField(default=False) 

  def get_username(self):
  	return self.username

  def get_id(self):
  	return self.id

  def get_diagnosis_perm(self):
    return self.diagnosis;

  def get_bp_reading_perm(self):
    return self.bp_reading

  def get_hr_reading_perm(self):
    return self.hr_reading

  def get_temp_reading_perm(self):
    return self.temp_reading

  def get_cancer_img_perm(self):
    return self.cancer_img

  def get_mri_img_perm(self):
    return self.mri_img

  def get_ultrasound_img_perm(self):
    return self.ultrasound_img

  def get_xray_img_perm(self):
    return self.xray_img

  def get_gastroscope_vid_perm(self):
    return self.gastroscope_vid

  def get_gait_vid_perm(self):
    return self.gait_vid
