from django import forms
from django_select2.forms import Select2MultipleWidget

class SearchRecordsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        tday = kwargs.pop('tday')
        RECORD_TYPES_PERMISSION = kwargs.pop('perm')
        super(SearchRecordsForm, self).__init__(*args, **kwargs)

        # Declare fields that require argument(s) from views
        self.fields['date'] = forms.CharField(
                required=True,
                label='Date',
                widget=forms.TextInput(attrs={'style':'width:100%'}),
                max_length=10,
                disabled=True,
                initial=tday
            )

        self.fields['recordtypes'] = forms.MultipleChoiceField(
                required=True,
                label='Record Types',
                widget=forms.CheckboxSelectMultiple,
                choices=RECORD_TYPES_PERMISSION
            )

    # Declare other fields

    age = forms.MultipleChoiceField(
                required=True,
                label='Age',
                widget=Select2MultipleWidget(attrs={'style':'width:100%', 'title':'Please input an age from 0 to 100'}),
                choices=list(zip(range(0, 101), range(0, 101)))
            )

    # Only first one is required
    postalcode1 = forms.CharField(
                required=True,
                label='Postal Code',
                widget=forms.TextInput(attrs={'pattern':'([0][1-9]|[1-6][0-9]|[7][0-3]|[7][5-9]|[8][0-2])[0-9]{4}', 'title':'Please input exactly 6 digits with a valid postalcode sector (i.e. starts with 01-73 or 75-82)', 'autocomplete':'off'}),
                min_length=6,
                max_length=6
        )

    postalcode2 = forms.CharField(
                required=False,
                widget=forms.TextInput(attrs={'pattern':'([0][1-9]|[1-6][0-9]|[7][0-3]|[7][5-9]|[8][0-2])[0-9]{4}', 'title':'Please input exactly 6 digits with a valid postalcode sector (i.e. starts with 01-73 or 75-82) or leave it empty', 'autocomplete':'off'}),
                min_length=6,
                max_length=6
        )

    postalcode3 = forms.CharField(
                required=False,
                widget=forms.TextInput(attrs={'pattern':'([0][1-9]|[1-6][0-9]|[7][0-3]|[7][5-9]|[8][0-2])[0-9]{4}', 'title':'Please input exactly 6 digits with a valid postalcode sector (i.e. starts with 01-73 or 75-82) or leave it empty', 'autocomplete':'off'}),
                min_length=6,
                max_length=6
        )

