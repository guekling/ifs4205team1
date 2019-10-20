from django import forms

class DeviceInforForm(forms.Form):
  infor = forms.CharField(widget=forms.PasswordInput(), required=True, max_length=128, min_length=128)
