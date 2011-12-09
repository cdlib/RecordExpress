from django import forms
from django.forms.formsets import formset_factory

from collection_record.ISO_639_2b import ISO_639_2b

class CollectionRecordForm(forms.Form):
#    ark = forms.CharField(max_length=255, initial='<Will be assigned>')
    title = forms.CharField(max_length=512, widget=forms.TextInput(attrs={'size':'100'},), label='Collection Title')
    title_filing = forms.CharField(max_length=256, label='Collection Title (Filing)', widget=forms.TextInput(attrs={'size':'100'},))
    date_dacs = forms.CharField(label='Collection Date')
    date_iso = forms.CharField(label='Collection Date (ISO 8601 Format)', help_text='Enter the dates normalized using the ISO 8601 format', required=False)
    local_identifier = forms.CharField(max_length=512, label='Collection Identifier/Call Number')
    extent=forms.CharField(widget=forms.TextInput(attrs={'size':'40'},), label='Extent of Collection')
    abstract=forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}))
    language = forms.ChoiceField(choices=(('eng', 'English'), ), initial='eng', label='Language of Materials')
    accessrestrict = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Access Conditions')
    userestrict = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Publication Rights')
    acqinfo = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Acquisition Information')
    bioghist = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Biography/Administrative History')
    scopecontent = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Scope and Content of Collection')
    online_items_url = forms.URLField(label='Online items URL', widget=forms.TextInput(attrs={'size':'110'},), required=False)

class CreatorPersonForm(forms.Form):
    term = forms.CharField(max_length=4, initial='CR', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='person', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Creator/Collector (Person)')
CreatorPersonFormset = formset_factory(CreatorPersonForm, extra=1)

class CreatorFamilyForm(forms.Form):
    term = forms.CharField(max_length=4, initial='CR', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='family', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Creator/Collector (Family)')
CreatorFamilyFormset = formset_factory(CreatorFamilyForm, extra=1)

class CreatorOrganizationForm(forms.Form):
    term = forms.CharField(max_length=4, initial='CR', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='organization', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Creator/Collector (Organization)')
CreatorOrganizationFormset = formset_factory(CreatorOrganizationForm, extra=1)

class SubjectTopicForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='topic', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Subject (Topic)')
SubjectTopicFormset = formset_factory(SubjectTopicForm, extra=1)

class SubjectPersonNameForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='person_name', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Subject (Personal name)')
SubjectPersonNameFormset = formset_factory(SubjectPersonNameForm, extra=1)

class SubjectFamilyNameForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='famaily_name', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Subject (Family name)')
SubjectFamilyNameFormset = formset_factory(SubjectFamilyNameForm, extra=1)

class SubjectOrganizationNameForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='organization_name', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Subject (Organization name)')
SubjectOrganizationNameFormset = formset_factory(SubjectOrganizationNameForm, extra=1)

class GeographicForm(forms.Form):
    term = forms.CharField(max_length=4, initial='COV', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='geog', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Subject (Geographical Location)')
GeographicFormset = formset_factory(GeographicForm, extra=1)

class GenreForm(forms.Form):
    term = forms.CharField(max_length=4, initial='TYP', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='genre', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Subject (Form/genre)')
GenreFormset = formset_factory(GenreForm, extra=1)

class SubjectTitleForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='title', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Subject (Titles)')
SubjectTitleFormset = formset_factory(SubjectTitleForm, extra=1)

class SubjectFunctionForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='function', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Subject (Functions)')
SubjectFunctionFormset = formset_factory(SubjectFunctionForm, extra=1)

class SubjectOccupationForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='occupation', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Subject (Occupations)')
SubjectOccupationFormset = formset_factory(SubjectOccupationForm, extra=1)

