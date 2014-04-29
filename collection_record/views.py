import urllib
import os
import json
import logging
import subprocess

from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse as django_url_reverse
#from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
import BeautifulSoup
from is_oac import is_OAC
OAC = is_OAC()
if OAC:
    from DSC_EZID_minter import main as EZIDMinter
from dublincore.models import QualifiedDublinCoreElement
from collection_record.models import CollectionRecord
from collection_record.models import SupplementalFile
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
from collection_record.forms import SupplementalFileForm
from collection_record.forms import SupplementalFileUploadForm
from collection_record.perm_backend import get_publishing_institutions_for_user

logger = logging.getLogger(__name__)

@never_cache
@login_required
def add_collection_record(request):
    '''Add a collection record. Must be a logged in user supplemental with a 
    publishing institution.
    '''
    choices_publishing_institution = [ (i.id, i.name) for i in get_publishing_institutions_for_user(request.user) ]
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
            #save collection and send to view/edit page?
            #check value of ark field in form. If it is blank or is still
            #the intial value, get a new ark
            # else validate ark or reject...
            ark = form_main.cleaned_data['ark']
            if ark == '' or ark == form_main.fields['ark'].initial:
                #mint an ark
                if OAC:
                    ark = EZIDMinter(1)[0]
                else:
                    ark = ''
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

def _url_xtf_preview(pk):
    import os
    import socket
    if os.environ.has_key('BACK_SERVER'): #OAC
        URL_THIS_SERVER = ''.join(('http://', os.environ.get('BACK_SERVER'), '/djsite/collection-record/' if OAC else '/collection-record/'))
    else:
        URL_THIS_SERVER = ''.join(('http://', socket.gethostbyname(socket.gethostname()), '/collection-record/'))
    URL_XTF_EAD_VIEW = ''.join(('http://', os.environ.get('FINDAID_HOSTNAME', 'www.oac.cdlib.org'), '/view?docId=ead-preview&doc.view=entire_text&source=', URL_THIS_SERVER))
    URL_XTF_EAD_VIEW_SUFFIX = '/xml/'
    return ''.join((URL_XTF_EAD_VIEW, str(pk), URL_XTF_EAD_VIEW_SUFFIX))

def handle_uploaded_file(collection_record, f, label=''):
    supp_file = SupplementalFile()
    supp_file.filename = f.name
    supp_file.collection_record = collection_record
    supp_file.label = label
    with supp_file.get_filehandle(mode='wb') as supp_file_obj:
        for chunk in f.chunks():
            supp_file_obj.write(chunk)
    if OAC:
        supp_file.rip_to_text()
    supp_file.save()
    return supp_file

@never_cache
@login_required
def edit_collection_record(request, *args, **kwargs):
    '''Formatted html view of the collection record with ark'''
    pagetitle = 'Edit Collection Record'
    if 'pk' in kwargs:
        collection_record = get_object_or_404(CollectionRecord, pk=kwargs['pk'])
    else:
        collection_record = get_object_or_404(CollectionRecord, ark=kwargs['ark'])
    #if not request.user.has_perm('collection_record.change_collectionrecord', collection_record):
    #    return  HttpResponseForbidden('<h1>Permission Denied</h1>')
    url_preview = _url_xtf_preview(collection_record.ark)
    dcformset_factory = generic_inlineformset_factory(QualifiedDublinCoreElement, extra=0, can_delete=True)
    supp_files_formset_factory = inlineformset_factory(CollectionRecord, SupplementalFile,  form=SupplementalFileForm, extra=0)
    choices_publishing_institution = [ (i.id, i.name) for i in get_publishing_institutions_for_user(request.user) ]
    upload_form = None
    if request.method == 'POST':
        #test if upload file?
        if 'label' in request.POST and request.FILES is not None:
            #file upload
            upload_form = SupplementalFileUploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                supp_file = handle_uploaded_file(collection_record, request.FILES['file'], label= upload_form.cleaned_data['label'])
        else: #main form submitted (could check the submit value too)
            form_main = CollectionRecordForm(request.POST, instance=collection_record)
            formset_person = dcformset_factory(request.POST, instance=collection_record, queryset=collection_record.creator_person, prefix='person')
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
            formset_organization.content_label = 'Organization Name'
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
            formset_supp_files = supp_files_formset_factory(request.POST, instance=collection_record)
            f=formset_supp_files.empty_form
            f.is_empty = True
            formset_supp_files.forms.append(f)
            formset_list = [ formset_person, formset_family, formset_organization,
                    formset_topic, formset_subject_person_name,
                    formset_subject_family_name, formset_subject_organization_name,
                    formset_geog, formset_genre, formset_subject_title,
                    formset_subject_function, formset_subject_occupation
                    ]
            valid_formsets = False not in [x.is_valid() for x in formset_list]  
            if form_main.is_valid() and valid_formsets and formset_supp_files.is_valid():
                form_main.save()
                #logger.debug('POST: %s' % (unicode(request.POST,)))
                for formset in formset_list:
                    for form in formset:
                        if form.is_valid():#DELTEs may not be valid
                            form.cleaned_data['qualifier'] = formset.qualifier
                    formset.save()
                formset_supp_files.save()
                return redirect(collection_record)
            else:
                formset_errors = ''
                if not valid_formsets:
                    for formset in formset_list:
                        formset_errors = ''.join((formset_errors, unicode(formset.errors)))
                if not formset_supp_files.is_valid():
                        formset_errors = ''.join((formset_errors, unicode(formset_supp_files.errors)))
                return render(request, 'collection_record/collection_record/edit.html',
                    locals(),
                )
    #NOT POST and post valid update
    if upload_form is None:
        upload_form = SupplementalFileUploadForm()
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
    formset_organization.content_label = 'Organization Name'
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

    formset_supp_files = supp_files_formset_factory(instance=collection_record)
    f=formset_supp_files.empty_form
    f.is_empty = True
    formset_supp_files.forms.append(f)
    return render(request, 'collection_record/collection_record/edit.html',
            locals(),
            )

@never_cache
#@login_required
def view_collection_record_xml(request, *args, **kwargs):
    '''XML view of collection record'''
    if 'pk' in kwargs:
        collection_record = get_object_or_404(CollectionRecord, pk=kwargs['pk'])
    else:
        collection_record = get_object_or_404(CollectionRecord, ark=kwargs['ark'])
    xml = collection_record.ead_xml
    response = HttpResponse(xml)
    response['Content-Type'] = 'application/xml; charset=utf-8'
    #response['Last-Modified'] = http_date(time.mktime(arkobject.dc_last_modified.timetuple()))
    return response

from django_sortable.helpers import sortable_helper

@never_cache
@login_required
def view_all_collection_records(request,):# *args, **kwargs):
    '''Formatted html of all collection records that are supplemental with
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
    collection_record_sortable = sortable_helper(request, object_list)
    return render(request, 'collection_record/collection_record/list.html',
            locals(),
            )

@never_cache
@login_required
def view_collection_record_oac_preview(request, *args, **kwargs):
    '''Proxy the xtf preview page'''
    if 'pk' in kwargs:
        collection_record = get_object_or_404(CollectionRecord, pk=kwargs['pk'])
    else:
        collection_record = get_object_or_404(CollectionRecord, ark=kwargs['ark'])
    url = _url_xtf_preview(collection_record.pk)
    collection_record = get_object_or_404(CollectionRecord, pk=collection_record.pk)
    foo = urllib.urlopen(url)
    html = foo.read()
    soup = BeautifulSoup.BeautifulSoup(html)
    body = soup.find('body')
    if request.user.has_perm('collection_record.change_collectionrecord', collection_record):
        edittag = BeautifulSoup.Tag(soup, 'a',
            attrs={'href':collection_record.get_edit_url(),
                'style':"""\
float:right;\
background-color:#C2492C;\
color:white;\
border-radius:10px;\
font-size:30px;\
margin:5px;\
text-decoration:none;\
padding:7px;\
font-family:inherit;\
vertical-align:baseline;\
line-height:1.5;\
""",
            } 
                    )
        edittag.insert(0, 'Edit')
        body.insert(0, edittag)
####  the close doesn't work due to security restrictions
    closetag = BeautifulSoup.Tag(soup, 'a',
            attrs={'href':django_url_reverse('collection_record_view_all'),
                'style':"""\
float:right;\
background-color:#C2492C;\
color:white;\
border-radius:10px;\
font-size:30px;\
margin:5px;\
text-decoration:none;\
padding:7px;\
font-family:inherit;\
vertical-align:baseline;\
line-height:1.5;\
""",
            } 
                    )
    closetag.insert(0, 'Close')
    body.insert(0, closetag)
    logouttag = BeautifulSoup.Tag(soup, 'a',
            attrs={'href':django_url_reverse('admin:logout'),
                'style':"""\
float:right;\
background-color:#C2492C;\
color:white;\
border-radius:10px;\
font-size:30px;\
margin:5px;\
text-decoration:none;\
padding:7px;\
font-family:inherit;\
vertical-align:baseline;\
line-height:1.5;\
""",
            } 
                    )
    logouttag.insert(0, 'Logout')
    body.insert(0, logouttag)
    return HttpResponse(soup.prettify()) # works
    #return HttpResponse(unicode(soup)) #does weird stuff to comments at end
    #return HttpResponse(soup.render_contents(indentLevel=2))# bad for unicode encoding?
