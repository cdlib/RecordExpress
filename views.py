# Create your views here.
from django.contrib.auth.decorators import permission_required, login_required

@login_required
#@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def add_collection_record(request):
    pass
