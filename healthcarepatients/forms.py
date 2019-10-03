from django import forms

from core.models import Healthcare

class HealthcareModelChoiceField(forms.ModelChoiceField):
  """
  Get full name of Healthcare objects in the ModelChoiceField
  """
  def label_from_instance(self, obj):
    return obj.username.get_full_name()

class TransferPatientForm(forms.Form):
  healthcare_professional = HealthcareModelChoiceField(queryset=Healthcare.objects.all(), required=True)