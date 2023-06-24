from django import forms


class ComposeForm(forms.Form):
    message = forms.CharField(widget=forms.TextInput())


class FileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput())