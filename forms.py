from django import forms
from django.forms.formsets import formset_factory

from collection_record.ISO_639_2b import ISO_639_2b

class CollectionRecordForm(forms.Form):
#    ark = forms.CharField(max_length=255, initial='<Will be assigned>')
    title = forms.CharField(max_length=512, widget=forms.TextInput(attrs={'size':'100'},), label='Collection Title')
    title_filing = forms.CharField(max_length=256, label='Collection Title (Filing)')
    date = forms.DateField(label='Collection Date')
    local_identifier = forms.CharField(max_length=512, label='Collection Identifier/Call Number')
    extent=forms.CharField(widget=forms.TextInput(attrs={'size':'40'},), label='Extent of Collection')
    abstract=forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}))
    language = forms.ChoiceField(choices=(('eng', 'English'), ), initial='eng', label='Language of Materials')
    accessrestrict = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Access Conditions')
    userestrict = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Publication Rights')
    acqinfo = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Acquisition Information')
    bioghist = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Biography/Administrative History')
    scopecontent = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Scopy and Content of Collection')
    online_items_url = forms.URLField(widget=forms.TextInput(attrs={'size':'100'},))

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

class SubjectNameForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='name', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Name of person, family or organization')
SubjectNameFormset = formset_factory(SubjectNameForm, extra=1)

class SubjectGeographicForm(forms.Form):
    term = forms.CharField(max_length=4, initial='SUB', widget=forms.HiddenInput)
    qualifier = forms.CharField(max_length=40, initial='geog', widget=forms.HiddenInput)
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Subject (Geographical Location)')
SubjectGeographicFormset = formset_factory(SubjectGeographicForm, extra=1)
