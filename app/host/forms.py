from django import forms

class TransientSearchForm(forms.Form):
    name = forms.CharField(label='',
                           widget=forms.TextInput(attrs={'placeholder': 'e.g. 2022eqw'}))




