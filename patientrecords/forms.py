from django import forms

from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, ReadingsPerm, TimeSeriesPerm, DocumentsPerm, ImagesPerm, VideosPerm

class ReadingsPermissionEditForm(forms.ModelForm):
  class Meta:
    model = ReadingsPerm
    fields = ['perm_value']

class TimeSeriesPermissionEditForm(forms.ModelForm):
  class Meta:
    model = TimeSeriesPerm
    fields = ['perm_value']

class DocumentsPermissionEditForm(forms.ModelForm):
  class Meta:
    model = DocumentsPerm
    fields = ['perm_value']

class VideosPermissionEditForm(forms.ModelForm):
  class Meta:
    model = VideosPerm
    fields = ['perm_value']

class ImagesPermissionEditForm(forms.ModelForm):
  class Meta:
    model = ImagesPerm
    fields = ['perm_value']

class CreateNewRecord(forms.Form):
  type_choices = [
    ('Readings', 'Readings'),
    ('TimeSeries', 'TimeSeries'),
    ('Images', 'Images'),
    ('Videos', 'Videos'),
    ('Documents', 'Documents'),
  ]
  type = forms.ChoiceField(choices=type_choices)

class CreateReadingsRecord(forms.ModelForm):
  type_choices = [
    ('Blood Pressure (BP)', 'Blood Pressure (BP)'),
    ('Heartrate', 'Heartrate'),
    ('Temperature', 'Temperature'),
  ]

  type = forms.ChoiceField(choices=type_choices)

  class Meta:
    model = Readings
    fields = ['data']

class CreateTimeSeriesRecord(forms.ModelForm):
  class Meta:
    model = TimeSeries
    fields = ['data']
  
class CreateImagesRecord(forms.ModelForm):
  type_choices = [
    ('Cancer', 'Cancer'),
    ('MRI', 'MRI'),
    ('Ultrasound', 'Ultrasound'),
    ('Xray', 'Xray'),
  ]

  type = forms.ChoiceField(choices=type_choices)

  class Meta:
    model = Images
    fields = ['title', 'data']

class CreateVideosRecord(forms.ModelForm):
  type_choices = [
    ('Gastroscope', 'Gastroscope'),
    ('Gait', 'Gait'),
  ]

  type = forms.ChoiceField(choices=type_choices)

  class Meta:
    model = Videos
    fields = ['title', 'data']

class CreateDocumentsRecord(forms.ModelForm):
  class Meta:
    model = Documents
    fields = ['title', 'data', 'type']