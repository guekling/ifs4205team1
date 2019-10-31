from django import forms

from core.models import Patient, Healthcare
from patientrecords.models import Readings, TimeSeries, Documents, Images, Videos

class HealthcareModelChoiceField(forms.ModelChoiceField):
  """
  Get full name of Healthcare objects in the ModelChoiceField
  """
  def label_from_instance(self, obj):
    return obj.username.username

class PatientModelChoiceField(forms.ModelChoiceField):
  """
  Get full name of Patient objects in the ModelChoiceField
  """
  def label_from_instance(self, obj):
    return obj.username.username

class TransferPatientForm(forms.Form):
  healthcare_professional = HealthcareModelChoiceField(queryset=Healthcare.objects.all(), required=True)

  def __init__(self,*args,**kwargs):
    self.patient = kwargs.pop('patient')
    super(TransferPatientForm, self).__init__(*args,**kwargs)
    hlistid = self.patient.healthcare_patients.all().values_list('id')
    self.fields['healthcare_professional'].queryset = Healthcare.objects.exclude(id__in=hlistid)

class CreateNewPatientRecord(forms.Form):
  type_choices = [
    ('Readings', 'Readings'),
    ('TimeSeries', 'TimeSeries'),
    ('Images', 'Images'),
    ('Videos', 'Videos'),
  ]
  type = forms.ChoiceField(choices=type_choices)
  patient = PatientModelChoiceField(queryset=Patient.objects.all(), required=True)

class CreatePatientReadingsRecord(forms.ModelForm):
  type_choices = [
    ('Blood Pressure (BP)', 'Blood Pressure (BP)'),
    ('Heartrate', 'Heartrate'),
    ('Temperature', 'Temperature'),
  ]

  type = forms.ChoiceField(choices=type_choices)

  class Meta:
    model = Readings
    fields = ['data']

class CreatePatientTimeSeriesRecord(forms.ModelForm):
  class Meta:
    model = TimeSeries
    fields = ['data']
  
class CreatePatientImagesRecord(forms.ModelForm):
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

class CreatePatientVideosRecord(forms.ModelForm):
  type_choices = [
    ('Gastroscope', 'Gastroscope'),
    ('Gait', 'Gait'),
  ]

  type = forms.ChoiceField(choices=type_choices)

  class Meta:
    model = Videos
    fields = ['title', 'data']