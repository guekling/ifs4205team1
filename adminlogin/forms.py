from django import forms

from core.models import User

class UserEditForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'email', 'dob', 'address', 'postalcode', 'contactnumber']

class UserQrForm(forms.Form):
  otp = forms.CharField(max_length=6)

class EditRecordTypesPermForm(forms.Form):
	def __init__(self, *args, **kwargs):
		recordtypes_choices = kwargs.pop('recordtypes_choices')
		recordtypes_perm = kwargs.pop('recordtypes_perm')
		super(EditRecordTypesPermForm, self).__init__(*args, **kwargs)

		self.fields['recordtypesperm'] = forms.MultipleChoiceField(
			required=False,
			label='Record Types Permission',
			widget=forms.CheckboxSelectMultiple,
			choices=recordtypes_choices,
			initial=recordtypes_perm
		)