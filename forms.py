from django import forms
from django.forms.formsets import formset_factory

from collection_record.ISO_639_2b import ISO_639_2b

class CollectionRecordForm(forms.Form):
#    ark = forms.CharField(max_length=255, initial='<Will be assigned>')
    title = forms.CharField(max_length=512)
    title_filing = forms.CharField(max_length=256)
    date = forms.DateField()
    local_identifier = forms.CharField(max_length=512)
    extent=forms.CharField()
    abstract=forms.CharField()
    language = forms.ChoiceField(choices=(('eng', 'English'), ), initial='eng')
    accessrestrict = forms.CharField()
    userestrict = forms.CharField()
    acqinfo = forms.CharField()
    bioghist = forms.CharField()
    scopecontent = forms.CharField()
    online_items_url = forms.URLField()

class CreatorPersonForm(forms.Form):
    term = forms.CharField(max_length=4, initial='CR', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='person', widget=forms.HiddenInput)
    content = forms.CharField()
CreatorPersonFormset = formset_factory(CreatorPersonForm, extra=1)

class CreatorFamilyForm(forms.Form):
    term = forms.CharField(max_length=4, initial='CR', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='family', widget=forms.HiddenInput)
    content = forms.CharField()
CreatorFamilyFormset = formset_factory(CreatorFamilyForm, extra=1)

class CreatorOrganizationForm(forms.Form):
    term = forms.CharField(max_length=4, initial='CR', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='organization', widget=forms.HiddenInput)
    content = forms.CharField()
CreatorOrganizationFormset = formset_factory(CreatorOrganizationForm, extra=1)

class SubjectTopicForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='topic', widget=forms.HiddenInput)
    content = forms.CharField()
SubjectTopicFormset = formset_factory(SubjectTopicForm, extra=1)

class SubjectNameForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='name', widget=forms.HiddenInput)
    content = forms.CharField()
SubjectNameFormset = formset_factory(SubjectNameForm, extra=1)

class SubjectGeographicForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='geog', widget=forms.HiddenInput)
    content = forms.CharField()
SubjectGeographicFormset = formset_factory(SubjectGeographicForm, extra=1)
