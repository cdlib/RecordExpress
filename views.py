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
from collection_record.forms import SubjectNameFormset 
from collection_record.forms import SubjectGeographicFormset 

@login_required
#@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def add_collection_record(request):
    if request.method == 'POST':
        form_main  = CollectionRecordForm(request.POST)
        formset_person = CreatorPersonFormset(request.POST, prefix='person') 
        formset_family = CreatorFamilyFormset(request.POST, prefix='family') 
        formset_organization = CreatorOrganizationFormset(request.POST, prefix='organization') 
        formset_topic = SubjectTopicFormset (request.POST, prefix='topic') 
        formset_subjectname = SubjectNameFormset (request.POST, prefix='subject_name') 
        formset_geog = SubjectGeographicFormset (request.POST, prefix='geog') 
        if form_main.is_valid() and formset_person.is_valid():
            if not request.POST.get('previewed', None):
                #preview it
                # create new unsaved obj from forms, include forms as hidden element?
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
        formset_topic = SubjectTopicFormset (prefix='topic') 
        formset_subjectname = SubjectNameFormset (prefix='subject_name') 
        formset_geog = SubjectGeographicFormset (prefix='geog') 
    return render(request,'collection_record/collection_record/add.html',
                              locals(),
                              )
