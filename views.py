import urllib
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.http import HttpResponse
from django.http import HttpResponse
#from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
import BeautifulSoup
from DSC_EZID_minter import main as EZIDMinter
from DublinCore.models import QualifiedDublinCoreElement
from collection_record.models import CollectionRecord
from collection_record.forms import CollectionRecordForm
from collection_record.forms import CollectionRecordAddForm
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
from collection_record.forms import CreatorPersonForm
from collection_record.forms import CreatorFamilyForm
from collection_record.forms import CreatorOrganizationForm
from collection_record.forms import SubjectTopicForm
from collection_record.forms import SubjectPersonNameForm
from collection_record.forms import SubjectFamilyNameForm
from collection_record.forms import SubjectOrganizationNameForm
from collection_record.forms import GeographicForm
from collection_record.forms import GenreForm
from collection_record.forms import SubjectTitleForm
from collection_record.forms import SubjectFunctionForm
from collection_record.forms import SubjectOccupationForm
from collection_record.perm_backend import get_publishing_institutions_for_user


def get_publishing_institution_choices_for_user(user):
    '''Return a tuple that represents the possible choices for publishing 
    institution for a given user
    '''
    pub_insts = get_publishing_institutions_for_user(user)
    choices = []
    for i in pub_insts:
        choices.append((i.id, i.name))
    return choices

@login_required
#@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def add_collection_record(request):
    '''Add a collection record. Must be a logged in user associated with a 
    publishing institution.
    '''
    choices_publishing_institution = get_publishing_institution_choices_for_user(request.user)
    if request.method == 'POST':
        form_main  = CollectionRecordAddForm(request.POST)
        form_main.fields['publishing_institution'].choices = choices_publishing_institution 
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
                preview = True
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
                collection_record.publisher_id = form_main.cleaned_data['publishing_institution']
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
                                content = form.cleaned_data['content']
                                qdce = QualifiedDublinCoreElement(term=form.term, qualifier=form.qualifier, content=content, content_object=collection_record)
                                qdce.full_clean()
                                qdce.save()
                            except KeyError:
                                pass
                return redirect(collection_record)
    else:
        form_main  = CollectionRecordAddForm()
        form_main.fields['publishing_institution'].choices = choices_publishing_institution 
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

def _url_xtf_preview(ark):
    import os
    URL_XTF_EAD_VIEW = 'http://' + os.environ['FINDAID_HOSTNAME']+'/view?docId=ead-preview&doc.view=entire_text&source=http://' + os.environ['BACK_SERVER'] + '/djsite/collection-record/'
    URL_XTF_EAD_VIEW_SUFFIX = '/xml/'
    return URL_XTF_EAD_VIEW + ark + URL_XTF_EAD_VIEW_SUFFIX

@login_required
#@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def edit_collection_record(request, ark, *args, **kwargs):
    '''Formatted html view of the collection record with ark'''
    pagetitle = 'Edit Collection Record'
    collection_record = get_object_or_404(CollectionRecord, ark=ark)
    url_preview = _url_xtf_preview(collection_record.ark)
    dcformset_factory = generic_inlineformset_factory(QualifiedDublinCoreElement, extra=0, can_delete=True)
    if request.method == 'POST':
        form_main = CollectionRecordForm(request.POST, instance=collection_record)
        #formset_person = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.creator_person, prefix='person')
        formset_person = dcformset_factory(request.POST, instance=collection_record, prefix='person')
        formset_person.qualifier = 'person'
        formset_person.term = 'CR'
        formset_person.content_label = 'Personal Name'
        formset_family = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.creator_family, prefix='family')
        formset_family.qualifier = 'family'
        formset_family.term = 'CR'
        formset_family.content_label = 'Family Name'
        formset_organization =dcformset_factory(request.POST, instance=collection_record, queryset= collection_record.creator_organization, prefix='organization')
        formset_organization.qualifier = 'organization'
        formset_organization.term = 'CR'
        formset_organization.content_label = 'Organization/Corporation Name'
        formset_topic = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.subject_topic, prefix='topic')
        formset_topic.qualifier = 'topic'
        formset_topic.term = 'SUB'
        formset_topic.content_label = 'Topical Term'
        formset_subject_person_name = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.subject_name_person, prefix='subject_person_name')
        formset_subject_person_name.qualifier = 'name_person'
        formset_subject_person_name.term = 'SUB'
        formset_subject_person_name.content_label = 'Subject Personal Name'
        formset_subject_family_name = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.subject_name_family, prefix='subject_family_name')
        formset_subject_family_name.qualifier = 'name_family'
        formset_subject_family_name.term = 'SUB'
        formset_subject_family_name.content_label = 'Subject Family Name'
        formset_subject_organization_name = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.subject_name_organization, prefix='subject_organization_name')
        formset_subject_organization_name.qualifier = 'name_organization'
        formset_subject_organization_name.term = 'SUB'
        formset_subject_organization_name.content_label = 'Subject Organization Name'
        formset_geog = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.coverage, prefix='geog')
        formset_geog.qualifier = 'geo'
        formset_geog.term = 'CVR'
        formset_geog.content_label = 'Geographical Location'
        formset_genre = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.type_format, prefix='genre')
        formset_genre.qualifier = 'genre'
        formset_genre.term = 'TYP'
        formset_genre.content_label = 'Form/Genre Term'
        formset_subject_title = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.subject_title, prefix='subject_title')
        formset_subject_title.qualifier = SubjectTitleForm.qualifier
        formset_subject_title.term = SubjectTitleForm.term
        formset_subject_title.content_label = SubjectTitleForm.content_label
        formset_subject_function = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.subject_function, prefix='subject_function')
        formset_subject_function.qualifier = 'function'
        formset_subject_function.term = 'SUB'
        formset_subject_function.content_label = 'Function Term'
        formset_subject_occupation = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.subject_occupation, prefix='subject_occupation')
        formset_subject_occupation.qualifier = 'occupation'
        formset_subject_occupation.term = 'SUB'
        formset_subject_occupation.content_label = 'Occupation Term'
        formset_list = [ formset_person, formset_family, formset_organization,
                formset_topic, formset_subject_person_name,
                formset_subject_family_name, formset_subject_organization_name,
                formset_geog, formset_genre, formset_subject_title,
                formset_subject_function, formset_subject_occupation
                ]
        valid_formsets = False not in [x.is_valid() for x in formset_list]  
        if form_main.is_valid() and valid_formsets:
            form_main.save()
            for formset in formset_list:
                for form in formset:
                    form.cleaned_data['qualifier'] = formset.qualifier
                formset.save()
        else:
            formset_errors = ''
            if not valid_formsets:
                for formset in formset_list:
                    formset_errors = ''.join((formset_errors, unicode(formset.errors)))
            return render(request, 'collection_record/collection_record/edit.html',
                locals(),
            )
    #NOT POST and post valid update
    form_main = CollectionRecordForm(instance=collection_record)
    formset_person = dcformset_factory(instance=collection_record, queryset=collection_record.creator_person, prefix='person')
    formset_family = dcformset_factory(instance=collection_record, queryset=collection_record.creator_family, prefix='family')
    formset_organization = dcformset_factory(instance=collection_record, queryset= collection_record.creator_organization, prefix='organization')
    formset_topic = dcformset_factory(instance=collection_record, queryset=collection_record.subject_topic, prefix='topic')
    formset_subject_person_name = dcformset_factory(instance=collection_record, queryset=collection_record.subject_name_person, prefix='subject_person_name')
    formset_subject_family_name = dcformset_factory(instance=collection_record, queryset=collection_record.subject_name_family, prefix='subject_family_name')
    formset_subject_organization_name = dcformset_factory(instance=collection_record, queryset=collection_record.subject_name_organization, prefix='subject_organization_name')
    formset_geog = dcformset_factory(instance=collection_record, queryset=collection_record.coverage, prefix='geog')
    formset_genre = dcformset_factory(instance=collection_record, queryset=collection_record.type_format, prefix='genre')
    formset_subject_title = dcformset_factory(instance=collection_record, queryset=collection_record.subject_title, prefix='subject_title')
    formset_subject_function = dcformset_factory(instance=collection_record, queryset=collection_record.subject_function, prefix='subject_function')
    formset_subject_occupation = dcformset_factory(instance=collection_record, queryset=collection_record.subject_occupation, prefix='subject_occupation')

    formset_person.qualifier = 'person'
    formset_person.term = 'CR'
    formset_person.content_label = 'Personal Name'
    formset_family.qualifier = 'family'
    formset_family.term = 'CR'
    formset_family.content_label = 'Family Name'
    formset_organization.qualifier = 'organization'
    formset_organization.term = 'CR'
    formset_organization.content_label = 'Organization/Corporation Name'
    formset_topic.qualifier = 'topic'
    formset_topic.term = 'SUB'
    formset_topic.content_label = 'Topical Term'
    formset_subject_person_name.qualifier = 'name_person'
    formset_subject_person_name.term = 'SUB'
    formset_subject_person_name.content_label = 'Subject Personal Name'
    formset_subject_family_name.qualifier = 'name_family'
    formset_subject_family_name.term = 'SUB'
    formset_subject_family_name.content_label = 'Subject Family Name'
    formset_subject_organization_name.qualifier = 'name_organization'
    formset_subject_organization_name.term = 'SUB'
    formset_subject_organization_name.content_label = 'Subject Organization Name'
    formset_geog.qualifier = 'geo'
    formset_geog.term = 'CVR'
    formset_geog.content_label = 'Geographical Location'
    formset_genre.qualifier = 'genre'
    formset_genre.term = 'TYP'
    formset_genre.content_label = 'Form/Genre Term'
    formset_subject_title.qualifier = SubjectTitleForm.qualifier
    formset_subject_title.term = SubjectTitleForm.term
    formset_subject_title.content_label = SubjectTitleForm.content_label
    formset_subject_function.qualifier = 'function'
    formset_subject_function.term = 'SUB'
    formset_subject_function.content_label = 'Function Term'
    formset_subject_occupation.qualifier = 'occupation'
    formset_subject_occupation.term = 'SUB'
    formset_subject_occupation.content_label = 'Occupation Term'
    formset_list = [ formset_person, formset_family, formset_organization,
                formset_topic, formset_subject_person_name,
                formset_subject_family_name, formset_subject_organization_name,
                formset_geog, formset_genre, formset_subject_title,
                formset_subject_function, formset_subject_occupation
                ]
    for formset in formset_list:
        f = formset.empty_form
        f.is_empty = True
        formset.forms.append(f)
        for form in formset:
            form.initial = {'term':formset.term, 'qualifier':formset.qualifier, 'content':form.instance.content}
            form.fields['content'].label = formset.content_label

    return render(request, 'collection_record/collection_record/edit.html',
            locals(),
            )

#@login_required
def view_collection_record_xml(request, ark, *args, **kwargs):
    '''XML view of collection record'''
    collection_record = get_object_or_404(CollectionRecord, ark=ark)
    xml = collection_record.ead_xml
    response = HttpResponse(xml)
    response['Content-Type'] = 'application/xml; charset=utf-8'
    #response['Last-Modified'] = http_date(time.mktime(arkobject.dc_last_modified.timetuple()))
    return response

@login_required
def view_all_collection_records(request,):# *args, **kwargs):
    '''Formatted html of all collection records that are associated with
    the logged in user's publishing institutions association.
    '''
    collection_records = CollectionRecord.objects.all()
    if request.user.is_superuser:
        user_records = collection_records
    else:
        #subset records based on user
        user_insts = get_publishing_institutions_for_user(request.user)
        user_records = []
        for rec in collection_records:
            if rec.publisher.id in [ inst.id for inst in user_insts]:
                user_records.append(rec)
    object_list = user_records #alias for Django generic view
    return render(request, 'collection_record/collection_record/list.html',
            locals(),
            )

@login_required
def view_collection_record_oac_preview(request, ark, *args, **kwargs):
    '''Proxy the xtf preview page'''
    url = _url_xtf_preview(ark)
    collection_record = get_object_or_404(CollectionRecord, ark=ark)
    foo = urllib.urlopen(url)
    html = foo.read()
    soup = BeautifulSoup.BeautifulSoup(html)
    body = soup.find('body')
    atag = BeautifulSoup.Tag(soup, 'a',
                    attrs={'style':"float:right;background-color:#C2492C;color:white;border-radius:10px;font-size:30px;margin:5px;text-decoration:none;padding:5px;", 'href':collection_record.get_edit_url()}
                    )
    atag.insert(0, 'Edit')
    body.insert(0, atag)
    return HttpResponse(soup.prettify()) # works
    #return HttpResponse(unicode(soup)) #does weird stuff to comments at end
    #return HttpResponse(soup.render_contents(indentLevel=2))# bad for unicode encoding?
