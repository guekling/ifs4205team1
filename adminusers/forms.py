from django import forms

from core.models import User, Patient

class PatientMultipleChoiceField(forms.ModelMultipleChoiceField):
  """
  Get full name of Patient objects in the ModelMultipleChoiceField
  """
  def label_from_instance(self, obj):
    return obj.username.get_full_name()

class CreateNewPatient(forms.ModelForm):
  gender_choices = [
    ('M', 'Male'),
    ('F', 'Female'),
  ]

  gender = forms.ChoiceField(choices=gender_choices)
  dob = forms.DateField(widget = forms.SelectDateWidget(years=range(1950, 2020)))
  password=forms.CharField(widget=forms.PasswordInput())
  confirm_password=forms.CharField(widget=forms.PasswordInput())

  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'email', 'username', 'dob', 'address', 'postalcode', 'contactnumber', 'password', 'gender']

  def clean(self):
    cleaned_data = super(CreateNewPatient, self).clean()
    password = cleaned_data.get("password")
    confirm_password = cleaned_data.get("confirm_password")

    if password != confirm_password:
      raise forms.ValidationError(
        "password and confirm_password does not match"
      )

class CreateNewHealthcare(forms.ModelForm):
  gender_choices = [
    ('M', 'Male'),
    ('F', 'Female'),
  ]

  license = forms.CharField(max_length=16, required=True)
  patients = PatientMultipleChoiceField(queryset=Patient.objects.all(), required=True)
  gender = forms.ChoiceField(choices=gender_choices)
  dob = forms.DateField(widget = forms.SelectDateWidget(years=range(1950, 2020)))
  password=forms.CharField(widget=forms.PasswordInput())
  confirm_password=forms.CharField(widget=forms.PasswordInput())

  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'email', 'username', 'dob', 'address', 'postalcode', 'contactnumber', 'password', 'gender']

  def clean(self):
    cleaned_data = super(CreateNewHealthcare, self).clean()
    password = cleaned_data.get("password")
    confirm_password = cleaned_data.get("confirm_password")

    if password != confirm_password:
      raise forms.ValidationError(
        "password and confirm_password does not match"
      )

class CreateNewResearcher(forms.ModelForm):
  gender_choices = [
    ('M', 'Male'),
    ('F', 'Female'),
  ]

  gender = forms.ChoiceField(choices=gender_choices)
  dob = forms.DateField(widget = forms.SelectDateWidget(years=range(1950, 2020)))
  password=forms.CharField(widget=forms.PasswordInput())
  confirm_password=forms.CharField(widget=forms.PasswordInput())

  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'email', 'username', 'dob', 'address', 'postalcode', 'contactnumber', 'password', 'gender']

  def clean(self):
    cleaned_data = super(CreateNewResearcher, self).clean()
    password = cleaned_data.get("password")
    confirm_password = cleaned_data.get("confirm_password")

    if password != confirm_password:
      raise forms.ValidationError(
        "password and confirm_password does not match"
      )