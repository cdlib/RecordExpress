# Create your views here.
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, get_object_or_404
#from django.shortcuts import get_object_or_404
#from django.http import HttpResponse
#from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
from collection_record.forms import NewCollectionRecordForm

@login_required
#@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def add_collection_record(request):
    if request.method == 'POST':
        form  = NewCollectionRecordForm(request.POST)
    else:
        form  = NewCollectionRecordForm()
    return render(request,'collection_record/collection_record/add.html',
                              locals(),
                              )
