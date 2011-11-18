from django.conf.urls.defaults import *

from collection_record.views import add_collection_record

urlpatterns = patterns('',
    url(r'^add', add_collection_record, name='collection_record_add'),
    )
