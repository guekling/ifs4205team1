from django import forms

from core.models import Healthcare
from patientrecords.models import DocumentsPerm

class HealthcareModelChoiceField(forms.ModelChoiceField):
  """
  Get full name of Healthcare objects in the ModelChoiceField
  """
  def label_from_instance(self, obj):
    return obj.username.username

class AddNotePermission(forms.ModelForm):
  PERMISSION_CHOICES = [
    (3, 'Full Access')
  ]

  perm_value = forms.ChoiceField(choices=PERMISSION_CHOICES, required=True)
  healthcare_professional = HealthcareModelChoiceField(queryset=Healthcare.objects.all(), required=True)

  class Meta:
    model = DocumentsPerm
    fields = ['perm_value']

  def __init__(self, *args, **kwargs):
    self.healthcare_list = kwargs.pop('healthcare_list')
    super(AddNotePermission, self).__init__(*args, **kwargs)
    self.fields['healthcare_professional'].queryset = self.healthcare_list