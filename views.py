# Create your views here.
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, get_object_or_404
#from django.shortcuts import get_object_or_404
#from django.http import HttpResponse
#from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
from collection_record.forms import CollectionRecordForm
from collection_record.forms import CreatorPersonFormset 
from collection_record.forms import CreatorFamilyFormset 

@login_required
#@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def add_collection_record(request):
    if request.method == 'POST':
        form  = CollectionRecordForm(request.POST)
        formset_person = CreatorPersonFormset(request.POST, prefix='person') 
        formset_family = CreatorFamilyFormset(request.POST, prefix='family') 
    else:
        form  = CollectionRecordForm()
        formset_person = CreatorPersonFormset(prefix='person') 
        formset_family = CreatorFamilyFormset(prefix='family') 
    return render(request,'collection_record/collection_record/add.html',
                              locals(),
                              )
