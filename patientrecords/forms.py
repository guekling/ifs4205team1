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
   