from django import forms
from django_bleach.models import BleachField

from core.models import Patient
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos, DocumentsPerm

##########################################
################# Fields #################
##########################################

class PatientModelChoiceField(forms.ModelChoiceField):
  """
  Get full name of Healthcare objects in the ModelChoiceField
  """
  def label_from_instance(self, obj):
    return obj.username.get_full_name()

class ReadingsMultipleChoiceField(forms.ModelMultipleChoiceField):

  def label_from_instance(self, obj):
    datetime = obj.timestamp.strftime("%a, %d %b %Y %I:%M %p")
    
    return datetime + " " + obj.type

class TimeSeriesMultipleChoiceField(forms.ModelMultipleChoiceField):

  def label_from_instance(self, obj):
    datetime = obj.timestamp.strftime("%a, %d %b %Y %I:%M %p")
    
    return datetime

class ImgVidMultipleChoiceField(forms.ModelMultipleChoiceField):

  def label_from_instance(self, obj):
    datetime = obj.timestamp.strftime("%a, %d %b %Y %I:%M %p")
    
    return datetime + " Type: " + obj.type + " Title: " + obj.title

class DocumentsPermissionEditForm(forms.ModelForm):
  class Meta:
    model = DocumentsPerm
    fields = ['perm_value']

class AddHealthcareNote(forms.Form):
  patient = PatientModelChoiceField(queryset=Patient.objects.all())
  
  def __init__(self,*args,**kwargs):
    self.healthcare = kwargs.pop('healthcare')
    super(AddHealthcareNote, self).__init__(*args,**kwargs)
    self.fields['patient'].queryset = Patient.objects.filter(healthcare_patients=self.healthcare)

class AddHealthcareNoteForPatient(forms.Form):
  title = forms.CharField()
  note = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}))
  attach_readings = ReadingsMultipleChoiceField(queryset=Readings.objects.all(), required=False)
  attach_timeseries = TimeSeriesMultipleChoiceField(queryset=TimeSeries.objects.all(), required=False)
  attach_images = ImgVidMultipleChoiceField(queryset=Images.objects.all(), required=False)
  attach_videos = ImgVidMultipleChoiceField(queryset=Videos.objects.all(), required=False)

  def __init__(self,*args,**kwargs):
    self.patient = kwargs.pop('patient')
    super(AddHealthcareNoteForPatient, self).__init__(*args,**kwargs)
    self.fields['attach_readings'].queryset = Readings.objects.filter(patient_id=self.patient)
    self.fields['attach_timeseries'].queryset = TimeSeries.objects.filter(patient_id=self.patient)
    self.fields['attach_images'].queryset = Images.objects.filter(patient_id=self.patient)
    self.fields['attach_videos'].queryset = Videos.objects.filter(patient_id=self.patient)

class EditHealthcareNote(forms.Form):
  title = forms.CharField()
  note = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}))
  # attach_readings = ReadingsMultipleChoiceField(queryset=Readings.objects.all(), required=False)
  # attach_timeseries = TimeSeriesMultipleChoiceField(queryset=TimeSeries.objects.all(), required=False)
  # attach_images = ImgVidMultipleChoiceField(queryset=Images.objects.all(), required=False)
  # attach_videos = ImgVidMultipleChoiceField(queryset=Videos.objects.all(), required=False)

  def __init__(self,*args,**kwargs):
    self.patient = kwargs.pop('patient')
    super(EditHealthcareNote, self).__init__(*args,**kwargs)
    # self.fields['attach_readings'].queryset = Readings.objects.filter(patient_id=self.patient)
    # self.fields['attach_timeseries'].queryset = TimeSeries.objects.filter(patient_id=self.patient)
    # self.fields['attach_images'].queryset = Images.objects.filter(patient_id=self.patient)
    # self.fields['attach_videos'].queryset = Videos.objects.filter(patient_id=self.patient)

    