from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
#from django.http import HttpResponse
#from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
from DSC_EZID_minter import main as EZIDMinter
from DublinCore.models import QualifiedDublinCoreElement
from collection_record.models import CollectionRecord
from collection_record.forms import CollectionRecordForm
from collection_record.forms import CreatorPersonFormset
from collection_record.forms import CreatorFamilyFormset
from collection_record.forms import CreatorOrganizationFormset
from collection_record.forms import SubjectTopicFormset
from collection_record.forms import SubjectPersonNameFormset
from collection_record.forms import SubjectFamilyNameFormset
from collection_record.forms import SubjectOrganizationNameFormset
from collection_record.forms import GeographicFormset
from collection_record.forms import GenreFormset
from collection_record.forms import SubjectTitleFormset
from collection_record.forms import SubjectFunctionFormset
from collection_record.forms import SubjectOccupationFormset


@login_required
#@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def add_collection_record(request):
    if request.method == 'POST':
        form_main  = CollectionRecordForm(request.POST)
        formset_person = CreatorPersonFormset(request.POST, prefix='person')
        formset_family = CreatorFamilyFormset(request.POST, prefix='family')
        formset_organization = CreatorOrganizationFormset(request.POST, prefix='organization')
        formset_topic = SubjectTopicFormset(request.POST, prefix='topic')
        formset_subject_person_name = SubjectPersonNameFormset(request.POST,
                prefix='subject_person_name')
        formset_subject_family_name = SubjectFamilyNameFormset(request.POST,
                prefix='subject_family_name')
        formset_subject_organization_name = SubjectOrganizationNameFormset(request.POST, prefix='subject_organization_name')
        formset_geog = GeographicFormset(request.POST, prefix='geog')
        formset_genre = GenreFormset(request.POST, prefix='genre')
        formset_subject_title = SubjectTitleFormset(request.POST, prefix='subject_title')
        formset_subject_function = SubjectFunctionFormset(request.POST, prefix='subject_function')
        formset_subject_occupation = SubjectOccupationFormset(request.POST, prefix='subject_occupation')
        formset_list = [ formset_person, formset_family, formset_organization,
                formset_topic, formset_subject_person_name,
                formset_subject_family_name, formset_subject_organization_name,
                formset_geog, formset_genre, formset_subject_title,
                formset_subject_function, formset_subject_occupation
                ]
        valid_formsets = False not in [x.is_valid() for x in formset_list]  
        if form_main.is_valid() and valid_formsets:
            if not request.POST.get('previewed', None):
                #preview it
                # create new unsaved obj from forms, include forms as hidden element?
                return render(request,'collection_record/collection_record/add_preview.html',
                              locals(),
                              )
            else:
                #save collection and send to view/edit page?
                # need to assign a new ark
                ark = EZIDMinter(1)[0]
                collection_record = CollectionRecord()
                collection_record.ark = ark
                collection_record.title = form_main.cleaned_data['title']
                collection_record.title_filing = form_main.cleaned_data['title_filing']
                collection_record.date_dacs = form_main.cleaned_data['date_dacs']
                collection_record.date_iso = form_main.cleaned_data['date_iso']
                collection_record.local_identifier = form_main.cleaned_data['local_identifier']
                collection_record.extent = form_main.cleaned_data['extent']
                collection_record.abstract = form_main.cleaned_data['abstract']
                collection_record.language = form_main.cleaned_data['language']
                collection_record.accessrestrict = form_main.cleaned_data['accessrestrict']
                collection_record.userestrict = form_main.cleaned_data['userestrict']
                collection_record.acqinfo = form_main.cleaned_data['acqinfo']
                collection_record.scopecontent = form_main.cleaned_data['scopecontent']
                collection_record.bioghist = form_main.cleaned_data['bioghist']
                collection_record.online_items_url = form_main.cleaned_data['online_items_url']
                collection_record.full_clean()
                collection_record.save()
                # Now handle the DC elements forms, we have a valid
                # collection record to associate the QDC with
                for formset in formset_list:
                    for form in formset:
                        if form.is_valid():
                            try:
                                term, qualifier, content = form.cleaned_data['term'], form.cleaned_data['qualifier'], form.cleaned_data['content']
                                qdce = QualifiedDublinCoreElement(term=term, qualifier=qualifier, content=content, content_object=collection_record)
                                qdce.save()
                            except KeyError:
                                pass
                return redirect(collection_record)
    else:
        form_main  = CollectionRecordForm()
        formset_person = CreatorPersonFormset(prefix='person')
        formset_family = CreatorFamilyFormset(prefix='family')
        formset_organization =CreatorOrganizationFormset(prefix='organization')
        formset_topic = SubjectTopicFormset(prefix='topic')
        formset_subject_person_name = SubjectPersonNameFormset(prefix='subject_person_name')
        formset_subject_family_name = SubjectFamilyNameFormset(prefix='subject_family_name')
        formset_subject_organization_name = SubjectOrganizationNameFormset(prefix='subject_organization_name')
        formset_geog = GeographicFormset(prefix='geog')
        formset_genre = GenreFormset(prefix='genre')
        formset_subject_title = SubjectTitleFormset(prefix='subject_title')
        formset_subject_function = SubjectFunctionFormset(prefix='subject_function')
        formset_subject_occupation = SubjectOccupationFormset(prefix='subject_occupation')
    return render(request,'collection_record/collection_record/add.html',
                              locals(),
                              )

@login_required
#@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def view_collection_record(request, ark, *args, **kwargs):
    collection_record = get_object_or_404(CollectionRecord, ark=ark)
    collection_record_dict = model_to_dict(collection_record)
    return render(request, 'collection_record/collection_record/view.html',
            locals(),
            )