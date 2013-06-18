from django import forms
from django.forms.formsets import formset_factory
from django.forms import ValidationError

from ARK_validator import validate, ARKInvalid

from collection_record.ISO_639_2b import ISO_639_2b
from collection_record.models import CollectionRecord
from collection_record.models import SupplementalFile

class CollectionRecordForm(forms.ModelForm):
    class Meta:
        model = CollectionRecord
        exclude = ('ark', 'publisher')

class CollectionRecordAddForm(forms.Form):
    ark = forms.CharField(initial='<Will be assigned>',
            required=False,
            help_text='If you have a previously assigned ARK add it here',
            label='ARK',
            max_length=CollectionRecord._meta.get_field_by_name('ark')[0].max_length,
            )
    title = forms.CharField(widget=forms.Textarea, label='Collection Title',
            help_text=''.join(('Maximum length: ',
                unicode(CollectionRecord._meta.get_field_by_name('title')[0].max_length),
                    )
                ),
            max_length=CollectionRecord._meta.get_field_by_name('title')[0].max_length,
            )
    title_filing = forms.CharField(label='Collection Title (Filing)',
            widget=forms.Textarea,
            help_text=''.join(('Maximum length: ',
                unicode(CollectionRecord._meta.get_field_by_name('title_filing')[0].max_length),
                    )
                ),
            max_length=CollectionRecord._meta.get_field_by_name('title_filing')[0].max_length,
            )
    publishing_institution = forms.ChoiceField(label="Publishing Institution")
    date_dacs = forms.CharField(label='Collection Date',
            help_text=''.join(('Maximum length: ',
                unicode(CollectionRecord._meta.get_field_by_name('date_dacs')[0].max_length),
                    )
                ),
            max_length=CollectionRecord._meta.get_field_by_name('date_dacs')[0].max_length,
            )
    date_iso = forms.CharField(label='Collection Date (ISO 8601 Format)',
                required=False,
                help_text=''.join(('Enter the dates normalized using the ISO 8601 format', 'Maximum length: ',
                unicode(CollectionRecord._meta.get_field_by_name('date_iso')[0].max_length),
                    )
                ),
            max_length=CollectionRecord._meta.get_field_by_name('date_iso')[0].max_length,
            )
    local_identifier = forms.CharField(label='Collection Identifier/Call Number',
            help_text=''.join(('Maximum length: ',
                unicode(CollectionRecord._meta.get_field_by_name('local_identifier')[0].max_length),
                    )
                ),
            max_length=CollectionRecord._meta.get_field_by_name('local_identifier')[0].max_length,
            )
    extent=forms.CharField(widget=forms.Textarea,
            label='Extent of Collection',
            help_text=''.join(('Maximum length: ',
                unicode(CollectionRecord._meta.get_field_by_name('extent')[0].max_length),
                    )
                ),
            max_length=CollectionRecord._meta.get_field_by_name('extent')[0].max_length,
            )
    abstract=forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}))
    language = forms.ChoiceField(choices=(ISO_639_2b), initial='eng', label='Language of Materials')
    accessrestrict = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Access Conditions')
    userestrict = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Publication Rights', required=False)
    acqinfo = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':'60',}), label='Acquisition Information', required=False)
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
                raise forms.ValidationError(unicode(e))
        return ark

class CreatorPersonForm(forms.Form):
    term = 'CR'
    qualifier = 'person'
    content = forms.CharField(widget=forms.Textarea, label='Personal Name')
CreatorPersonFormset = formset_factory(CreatorPersonForm, extra=1)

class CreatorFamilyForm(forms.Form):
    term = 'CR'
    qualifier = 'family'
    content = forms.CharField(widget=forms.Textarea, label='Family Name')
CreatorFamilyFormset = formset_factory(CreatorFamilyForm, extra=1)

class CreatorOrganizationForm(forms.Form):
    term = 'CR'
    qualifier = 'organization'
    content = forms.CharField(widget=forms.Textarea, label='Organization Name')
CreatorOrganizationFormset = formset_factory(CreatorOrganizationForm, extra=1)

class SubjectTopicForm(forms.Form):
    term = 'SUB'
    qualifier = 'topic'
    content_label = 'Topical Term'
    content = forms.CharField(label=content_label, widget=forms.Textarea) #widget=forms.Textarea(attrs={'rows':3, 'cols':'60',})) 
SubjectTopicFormset = formset_factory(SubjectTopicForm, extra=1)

class SubjectPersonNameForm(forms.Form):
    term = 'SUB'
    qualifier = 'name_person'
    content = forms.CharField(widget=forms.Textarea, label='Personal Name')
SubjectPersonNameFormset = formset_factory(SubjectPersonNameForm, extra=1)

class SubjectFamilyNameForm(forms.Form):
    term = 'SUB'
    qualifier = 'name_family'
    content = forms.CharField(widget=forms.Textarea, label='Family Name')
SubjectFamilyNameFormset = formset_factory(SubjectFamilyNameForm, extra=1)

class SubjectOrganizationNameForm(forms.Form):
    term = 'SUB'
    qualifier = 'name_organization'
    content = forms.CharField(widget=forms.Textarea, label='Organization Name')
SubjectOrganizationNameFormset = formset_factory(SubjectOrganizationNameForm, extra=1)

class GeographicForm(forms.Form):
    term = 'CVR'
    qualifier = 'geo'
    content = forms.CharField(widget=forms.Textarea, label='Geographical Location')
GeographicFormset = formset_factory(GeographicForm, extra=1)

class GenreForm(forms.Form):
    term = 'TYP'
    qualifier = 'genre'
    content = forms.CharField(widget=forms.Textarea, label='Form/Genre Term')
GenreFormset = formset_factory(GenreForm, extra=1)

class SubjectTitleForm(forms.Form):
    term = 'SUB'
    qualifier = 'title'
    content_label = 'Title'
    content = forms.CharField( label=content_label, widget=forms.Textarea) #widget=forms.Textarea(attrs={'rows':3, 'cols':'60',})) 
SubjectTitleFormset = formset_factory(SubjectTitleForm, extra=1)

class SubjectFunctionForm(forms.Form):
    term = 'SUB'
    qualifier = 'function'
    content = forms.CharField(widget=forms.Textarea, label='Function Term')
SubjectFunctionFormset = formset_factory(SubjectFunctionForm, extra=1)

class SubjectOccupationForm(forms.Form):
    term = 'SUB'
    qualifier = 'occupation'
    content = forms.CharField(widget=forms.Textarea, label='Occupation')
SubjectOccupationFormset = formset_factory(SubjectOccupationForm, extra=1)

class SupplementalFileForm(forms.ModelForm):
    class Meta:
        model = SupplementalFile
        widgets = {
                'filename': forms.HiddenInput,
                }

class SupplementalFileUploadForm(forms.Form):
    label = forms.CharField(max_length=512)
    file  = forms.FileField(widget=forms.FileInput(attrs={'accept':'application/pdf'}))

    def clean_file(self):
        '''Verify that it is a pdf being uploaded. How tricky should I get here?
        '''
        f = self.cleaned_data['file']
        if f.content_type != 'application/pdf':
            msg = "Only pdf files allowed for upload"
            self._errors["file"] = self.error_class([msg])
            raise ValidationError(msg)
        #TODO: add a check of actual file contents
        #probably easiest using pyPdf.PdfFileReader
        #maybe best to do this in the handle function
        return f
