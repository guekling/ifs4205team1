import uuid

from django.core.validators import FileExtensionValidator
from django.db import models
from core.models import User, Patient, Healthcare

class Readings(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  type = models.CharField(max_length=64)
  timestamp = models.DateTimeField(auto_now=True)
  owner_id = models.ForeignKey( # many readings related to one user
    User,
    on_delete=models.PROTECT,
    related_name='readings_owner'
  )
  patient_id = models.ForeignKey( # many readings related to one patient
    Patient,
    on_delete=models.CASCADE,
    related_name='readings_patient'
  )
  data = models.CharField(max_length=15)

  def has_permission(self, healthcare):
    """
    Checks if a user has permissions to view the reading.
    """

    reading = ReadingsPerm.objects.filter(readings_id = self, username=healthcare)

    if (reading.count() == 0):
      return False
    else:
      return True

class ReadingsPerm(models.Model):
  PERMISSION_CHOICES = [
    (1, 'No Access'),
    (2, 'Read Only Access'),
    (3, 'Full Access'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  readings_id = models.ForeignKey( # many permissions related to one reading
    Readings,
    on_delete=models.CASCADE,
    related_name='readingsperm_reading'
  )
  username = models.ManyToManyField(Healthcare)
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name='readingsperm_given_by'
  )
  perm_value = models.PositiveSmallIntegerField(choices=PERMISSION_CHOICES)
  (('readings_id', 'username'),)

class TimeSeries(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  timestamp = models.DateTimeField(auto_now=True)
  owner_id = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name='timeseries_owner'
    )
  patient_id = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE,
    related_name='timeseries_patient'
  )
  data = models.FileField(upload_to='timeseries/', validators=[FileExtensionValidator(allowed_extensions=['txt'])])

  def has_permission(self, healthcare):
    """
    Checks if a user has permissions to view the timeseries.
    """

    timeseries = TimeSeriesPerm.objects.filter(timeseries_id = self, username=healthcare)

    if (timeseries.count() == 0):
      return False
    else:
      return True

class TimeSeriesPerm(models.Model):
  PERMISSION_CHOICES = [
    (1, 'No Access'),
    (2, 'Read Only Access'),
    (3, 'Full Access'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  timeseries_id = models.ForeignKey(
    TimeSeries,
    on_delete=models.CASCADE,
    related_name='timeseriesperm_timeseries'
  )
  username = models.ManyToManyField(Healthcare)
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name='timeseriesperm_given_by'
  )
  perm_value = models.PositiveSmallIntegerField(choices=PERMISSION_CHOICES)
  (('timeseries_id', 'username'),)

class Videos(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=64)
  type = models.CharField(max_length=64)
  timestamp = models.DateTimeField(auto_now=True)
  owner_id = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name='videos_owner'
  )
  patient_id = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE,
    related_name='videos_patient'
  )
  data = models.FileField(upload_to='videos/', validators=[FileExtensionValidator(allowed_extensions=['mp4'])])

  def has_permission(self, healthcare):
    """
    Checks if a user has permissions to view the video.
    """

    video = VideosPerm.objects.filter(videos_id = self, username=healthcare)

    if (video.count() == 0):
      return False
    else:
      return True

class VideosPerm(models.Model):
  PERMISSION_CHOICES = [
    (1, 'No Access'),
    (2, 'Read Only Access'),
    (3, 'Full Access'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  videos_id = models.ForeignKey(
    Videos,
    on_delete=models.CASCADE,
    related_name='videosperm_videos'
  )
  username = models.ManyToManyField(Healthcare)
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name='videosperm_given_by'
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
    on_delete=models.PROTECT,
    related_name='images_owner'
  )
  patient_id = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE,
    related_name='images_patient'
  )
  data = models.ImageField(upload_to='images/')

  def has_permission(self, healthcare):
    """
    Checks if a user has permissions to view the reading.
    """

    image = ImagesPerm.objects.filter(img_id = self, username=healthcare)

    if (image.count() == 0):
      return False
    else:
      return True

class ImagesPerm(models.Model):
  PERMISSION_CHOICES = [
    (1, 'No Access'),
    (2, 'Read Only Access'),
    (3, 'Full Access'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  img_id = models.ForeignKey(
    Images,
    on_delete=models.CASCADE,
    related_name='imagesperm_images'
  )
  username = models.ManyToManyField(Healthcare)
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name='imagessperm_given_by'
  )
  perm_value = models.PositiveSmallIntegerField(choices=PERMISSION_CHOICES)
  unique_together = (('img_id', 'username'),)

class Diagnosis(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=64)
  time_start = models.DateTimeField(auto_now_add=True)
  time_end = models.DateTimeField(null=True)
  owner_id = models.ForeignKey( # many diagnosis related to one user
    User,
    on_delete=models.PROTECT,
    related_name='diagnosis_owner'
  )
  patient_id = models.ForeignKey( # many readings related to one patient
    Patient,
    on_delete=models.CASCADE,
    related_name='diagnosis_patient'
  )

  def has_permission(self, healthcare):
    """
    Checks if a user has permissions to view the diagnosis.
    """

    diagnosis = DiagnosisPerm.objects.filter(diag_id = self, username=healthcare)

    if (diagnosis.count() == 0):
      return False
    else:
      return True

class DiagnosisPerm(models.Model):
  PERMISSION_CHOICES = [
    (1, 'No Access'),
    (2, 'Read Only Access'),
    (3, 'Full Access'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  diag_id = models.ForeignKey(
    Diagnosis,
    on_delete=models.CASCADE,
    related_name='diagnosisperm_diag'
  )
  username = models.ManyToManyField(Healthcare)
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name='diagnosisperm_given_by'
  )
  perm_value = models.PositiveSmallIntegerField(choices=PERMISSION_CHOICES)
  unique_together = (('diag_id', 'username'),)

class Documents(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=64)
  type = models.CharField(max_length=64)
  timestamp = models.DateTimeField(auto_now=True)
  owner_id = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name='documents_owner'
  )
  patient_id = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE,
    related_name='documents_patient'
  )
  data = models.FileField(upload_to='documents/')
  attach_readings = models.ManyToManyField(Readings)
  attach_timeseries = models.ManyToManyField(TimeSeries)
  attach_videos = models.ManyToManyField(Videos)
  attach_images = models.ManyToManyField(Images)
  attach_documents = models.ManyToManyField("self")

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
    (3, 'Full Access'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  docs_id = models.ForeignKey(
    Documents,
    on_delete=models.CASCADE,
    related_name='documentsperm_documents'
  )
  username = models.ManyToManyField(User)
  timestamp = models.DateTimeField(auto_now=True)
  given_by = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name='documentsperm_given_by'
  )
  perm_value = models.PositiveSmallIntegerField(choices=PERMISSION_CHOICES)
  (('docs_id', 'username'),)