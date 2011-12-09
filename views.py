# Create your views here.
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, get_object_or_404
#from django.shortcuts import get_object_or_404
#from django.http import HttpResponse
#from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
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
        if form_main.is_valid() and formset_person.is_valid():
            if not request.POST.get('previewed', None):
                #preview it
                # create new unsaved obj from forms, include forms as hidden element?
                return render(request,'collection_record/collection_record/add.html',
                              locals(),
                              )
                return render(request,'collection_record/collection_record/add_preview.html',
                              locals(),
                              )
            else:
                pass #save collection and send to view/edit page?
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
