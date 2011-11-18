from django import forms

class NewCollectionRecordForm(forms.Form):
    ark = forms.CharField(max_length=255)
    title = forms.CharField(max_length=1024)
