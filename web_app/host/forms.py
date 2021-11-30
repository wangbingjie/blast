from django import forms

class TransientForm(forms.Form):
    name = forms.CharField(label='Transient Name:')
    ra = forms.DecimalField(label='RA [deg]:')
    dec = forms.DecimalField(label='Dec [deg]:')




