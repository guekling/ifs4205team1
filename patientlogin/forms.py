from django import forms

from core.models import User

class UserEditForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'email', 'dob', 'address', 'postalcode', 'contactnumber']