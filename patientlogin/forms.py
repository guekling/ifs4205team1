from django import forms

from core.models import User

class UserEditForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'email', 'dob', 'address', 'postalcode', 'contactnumber']

class UserQrForm(forms.Form):
  otp = forms.CharField(max_length=6)