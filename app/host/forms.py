from django import forms


class TransientSearchForm(forms.Form):
    name = forms.CharField(
        label="", widget=forms.TextInput(attrs={"placeholder": "e.g. 2022eqw"})
    )


class ImageGetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        filter_choices = kwargs.pop("filter_choices")
        super(ImageGetForm, self).__init__(*args, **kwargs)
        choices = [(filter, filter) for filter in filter_choices]
        choices.insert(0, (None, "Choose cutout"))
        self.fields["filters"] = forms.ChoiceField(
            label="",
            choices=choices,
            widget=forms.Select(attrs={"placeholder": "select cutout"}),
        )
