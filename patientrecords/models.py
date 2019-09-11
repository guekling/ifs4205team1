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
  perm_value = models.PositiveSmallIntegerField() # only digits 1,2,3,4 (logically, only 2,3)
  unique_together = (('readings_id', 'username'),)

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
  data = models.FileField(upload_to='media/timeseries/') # txt files

class TimeSeriesPerm(models.Model):
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
  perm_value = models.PositiveSmallIntegerField() # only digits 1,2,3,4 (logically, only 2,3)
  unique_together = (('timeseries_id', 'username'),)

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
  data = models.FileField(upload_to='media/documents/')

class DocumentsPerm(models.Model):
  docs_id = models.ForeignKey(
    Documents,
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
  perm_value = models.PositiveSmallIntegerField() # only digits 1,2,3,4 (logically, only 2,3)
  unique_together = (('docs_id', 'username'),)

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
  data = models.FileField(upload_to='media/videos/')

class VideosPerm(models.Model):
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
  perm_value = models.PositiveSmallIntegerField() # only digits 1,2,3,4 (logically, only 2,3)
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
  data = models.ImageField(upload_to='media/images/')

class ImagesPerm(models.Model):
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
  perm_value = models.PositiveSmallIntegerField() # only digits 1,2,3,4 (logically, only 2,3)
  unique_together = (('img_id', 'username'),)

class Diagnosis(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=64)
  time_start = models.DateTimeField(auto_now_add=True)
  time_end = models.DateTimeField()
  username = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE)

class DiagPerm(models.Model):
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
  perm_value = models.PositiveSmallIntegerField() # only digits 1,2,3,4 (logically, only 2,3)
  unique_together = (('diag_id', 'username'),)
