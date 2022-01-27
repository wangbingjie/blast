from django import forms

class TransientSearchForm(forms.Form):
    name = forms.CharField(label='Transient Name')




