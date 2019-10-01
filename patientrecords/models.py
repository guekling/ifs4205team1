import uuid

from django.db import models
from core.models import User, Patient, Healthcare

class Readings(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  type = models.CharField(max_length=64)
  timestamp = models.DateTimeField(auto_now=True)
  owner_id = models.ForeignKey( # many readings related to one user
    User,
    on_delete=models.PROTECT
    )
  patient_id = models.ForeignKey( # many readings related to one patient
    Patient,
    on_delete=models.CASCADE)
  data = models.DecimalField(max_digits=10, decimal_places=2)

class ReadingsPerm(models.Model):
  PERMISSION_CHOICES = [
    (1, 'No Access'),
    (2, 'Read Only Access'),
    (3, 'Read & Set Permissions Access'),
    (4, 'Owner'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  readings_id = models.ForeignKey( # many permissions related to one reading
    Readings,
    on_delete=models.CASCADE
  )
  username = models.ForeignKey(
    Healthcare,
    on_delete=models.CASCADE
  )
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT
  )
  perm_value = models.PositiveSmallIntegerField(choices=PERMISSION_CHOICES)
  (('readings_id', 'username'),)

class TimeSeries(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  timestamp = models.DateTimeField(auto_now=True)
  owner_id = models.ForeignKey(
    User,
    on_delete=models.PROTECT
    )
  patient_id = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE)
  data = models.FileField(upload_to='timeseries/') # txt files

class TimeSeriesPerm(models.Model):
  PERMISSION_CHOICES = [
    (1, 'No Access'),
    (2, 'Read Only Access'),
    (3, 'Read & Set Permissions Access'),
    (4, 'Owner'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  timeseries_id = models.ForeignKey(
    TimeSeries,
    on_delete=models.CASCADE
  )
  username = models.ForeignKey(
    Healthcare,
    on_delete=models.CASCADE
  )
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT
  )
  perm_value = models.PositiveSmallIntegerField(choices=PERMISSION_CHOICES)
  (('timeseries_id', 'username'),)

class Documents(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=64)
  type = models.CharField(max_length=64)
  timestamp = models.DateTimeField(auto_now=True)
  owner_id = models.ForeignKey(
    User,
    on_delete=models.PROTECT
  )
  patient_id = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE)
  data = models.FileField(upload_to='documents/')

  def has_permission(self, user):
    """
    Checks if a user has permissions to view the document.
    """

    document = DocumentsPerm.objects.filter(docs_id = self, username=user)

    if (document.count() == 0):
      return False
    else:
      return True

class DocumentsPerm(models.Model):
  PERMISSION_CHOICES = [
    (1, 'No Access'),
    (2, 'Read Only Access'),
    (3, 'Read & Set Permissions Access'),
    (4, 'Owner'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  docs_id = models.ForeignKey(
    Documents,
    on_delete=models.CASCADE
  )
  username = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='get_users'
  )
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name='get_given_by'
  )
  perm_value = models.PositiveSmallIntegerField(choices=PERMISSION_CHOICES)
  (('docs_id', 'username'),)

class Videos(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=64)
  type = models.CharField(max_length=64)
  timestamp = models.DateTimeField(auto_now=True)
  owner_id = models.ForeignKey(
    User,
    on_delete=models.PROTECT
    )
  patient_id = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE)
  data = models.FileField(upload_to='videos/')

class VideosPerm(models.Model):
  PERMISSION_CHOICES = [
    (1, 'No Access'),
    (2, 'Read Only Access'),
    (3, 'Read & Set Permissions Access'),
    (4, 'Owner'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  videos_id = models.ForeignKey(
    Videos,
    on_delete=models.CASCADE
  )
  username = models.ForeignKey(
    Healthcare,
    on_delete=models.CASCADE
  )
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT
  )
  perm_value = models.PositiveSmallIntegerField(choices=PERMISSION_CHOICES)
  unique_together = (('videos_id', 'username'),)

class Images(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=64)
  type = models.CharField(max_length=64)
  timestamp = models.DateTimeField(auto_now=True)
  owner_id = models.ForeignKey(
    User,
    on_delete=models.PROTECT
    )
  patient_id = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE)
  data = models.ImageField(upload_to='images/')

class ImagesPerm(models.Model):
  PERMISSION_CHOICES = [
    (1, 'No Access'),
    (2, 'Read Only Access'),
    (3, 'Read & Set Permissions Access'),
    (4, 'Owner'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  img_id = models.ForeignKey(
    Images,
    on_delete=models.CASCADE
  )
  username = models.ForeignKey(
    Healthcare,
    on_delete=models.CASCADE
  )
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT
  )
  perm_value = models.PositiveSmallIntegerField(choices=PERMISSION_CHOICES)
  unique_together = (('img_id', 'username'),)

class Diagnosis(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=64)
  time_start = models.DateTimeField(auto_now_add=True)
  time_end = models.DateTimeField()
  username = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE)

class DiagnosisPerm(models.Model):
  PERMISSION_CHOICES = [
    (1, 'No Access'),
    (2, 'Read Only Access'),
    (3, 'Read & Set Permissions Access'),
    (4, 'Owner'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  diag_id = models.ForeignKey(
    Diagnosis,
    on_delete=models.CASCADE
  )
  username = models.ForeignKey(
    Healthcare,
    on_delete=models.CASCADE
  )
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT
  )
  perm_value = models.PositiveSmallIntegerField(choices=PERMISSION_CHOICES)
  unique_together = (('diag_id', 'username'),)
