from django import forms
from django.forms.formsets import formset_factory

from ARK_validator import validate, ARKInvalid

from collection_record.ISO_639_2b import ISO_639_2b
from collection_record.models import CollectionRecord
from collection_record.models import SupplementalFile

class CollectionRecordForm(forms.ModelForm):
    class Meta:
        model = CollectionRecord
        exclude = ('ark', )

class CollectionRecordAddForm(forms.Form):
    ark = forms.CharField(max_length=255, initial='<Will be assigned>',
            required=False,
            help_text='If you have a previously assigned ARK add it here',
            label='ARK')
    title = forms.CharField(max_length=512, widget=forms.TextInput(attrs={'size':'100'},), label='Collection Title')
    title_filing = forms.CharField(max_length=256, label='Collection Title (Filing)', widget=forms.TextInput(attrs={'size':'100'},))
    publishing_institution = forms.ChoiceField()
    date_dacs = forms.CharField(label='Collection Date')
    date_iso = forms.CharField(label='Collection Date (ISO 8601 Format)', help_text='Enter the dates normalized using the ISO 8601 format', required=False)
    local_identifier = forms.CharField(max_length=512, label='Collection Identifier/Call Number')
    extent=forms.CharField(widget=forms.TextInput(attrs={'size':'40'},), label='Extent of Collection')
    abstract=forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}))
    language = forms.ChoiceField(choices=(ISO_639_2b), initial='eng', label='Language of Materials')
    accessrestrict = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Access Conditions')
    userestrict = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Publication Rights')
    acqinfo = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Acquisition Information')
    scopecontent = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Scope and Content of Collection')
    bioghist = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Biography/Administrative History', required=False)
    online_items_url = forms.URLField(label='Online Items URL', widget=forms.TextInput(attrs={'size':'110'},), required=False)

    def clean_ark(self):
        ark = self.cleaned_data['ark']
        if not( ark == '' or ark == self.fields['ark'].initial):
            #not blank or initial value, validate the ark
            try:
                ark, NAAN, name, qualifier = validate(ark)
            except ARKInvalid, e:
                raise forms.ValidationError(str(e))
        return ark

class CreatorPersonForm(forms.Form):
    term = 'CR'
    qualifier = 'person'
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Personal Name')
CreatorPersonFormset = formset_factory(CreatorPersonForm, extra=1)

class CreatorFamilyForm(forms.Form):
    term = 'CR'
    qualifier = 'family'
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Family Name')
CreatorFamilyFormset = formset_factory(CreatorFamilyForm, extra=1)

class CreatorOrganizationForm(forms.Form):
    term = 'CR'
    qualifier = 'organization'
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Organization Name')
CreatorOrganizationFormset = formset_factory(CreatorOrganizationForm, extra=1)

class SubjectTopicForm(forms.Form):
    term = 'SUB'
    qualifier = 'topic'
    content_label = 'Topical Term'
    content = forms.CharField(max_length=40, label=content_label, widget=forms.TextInput(attrs={'size':'60',})) #widget=forms.Textarea(attrs={'rows':3, 'cols':'60',})) 
SubjectTopicFormset = formset_factory(SubjectTopicForm, extra=1)

class SubjectPersonNameForm(forms.Form):
    term = 'SUB'
    qualifier = 'name_person'
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Personal Name')
SubjectPersonNameFormset = formset_factory(SubjectPersonNameForm, extra=1)

class SubjectFamilyNameForm(forms.Form):
    term = 'SUB'
    qualifier = 'name_family'
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Family Name')
SubjectFamilyNameFormset = formset_factory(SubjectFamilyNameForm, extra=1)

class SubjectOrganizationNameForm(forms.Form):
    term = 'SUB'
    qualifier = 'name_organization'
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Organization Name')
SubjectOrganizationNameFormset = formset_factory(SubjectOrganizationNameForm, extra=1)

class GeographicForm(forms.Form):
    term = 'CVR'
    qualifier = 'geo'
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Geographical Location')
GeographicFormset = formset_factory(GeographicForm, extra=1)

class GenreForm(forms.Form):
    term = 'TYP'
    qualifier = 'genre'
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Form/Genre Term')
GenreFormset = formset_factory(GenreForm, extra=1)

class SubjectTitleForm(forms.Form):
    term = 'SUB'
    qualifier = 'title'
    content_label = 'Title'
    content = forms.CharField(max_length=40, label=content_label, widget=forms.TextInput(attrs={'size':'60',})) #widget=forms.Textarea(attrs={'rows':3, 'cols':'60',})) 
SubjectTitleFormset = formset_factory(SubjectTitleForm, extra=1)

class SubjectFunctionForm(forms.Form):
    term = 'SUB'
    qualifier = 'function'
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Function Term')
SubjectFunctionFormset = formset_factory(SubjectFunctionForm, extra=1)

class SubjectOccupationForm(forms.Form):
    term = 'SUB'
    qualifier = 'occupation'
    content = forms.CharField(widget=forms.TextInput(attrs={'size':'60',}), label='Occupation')
SubjectOccupationFormset = formset_factory(SubjectOccupationForm, extra=1)

class SupplementalFileForm(forms.ModelForm):
    class Meta:
        model = SupplementalFile
        widgets = {
                'filename': forms.HiddenInput,
                }

class SupplementalFileUploadForm(forms.Form):
    label = forms.CharField(max_length=512)
    file  = forms.FileField()
