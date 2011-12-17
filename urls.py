from django.conf.urls.defaults import *

from collection_record.views import add_collection_record
from collection_record.views import view_collection_record

urlpatterns = patterns('',
    url(r'^add', add_collection_record, name='collection_record_add'),
    url(r'^(?P<ark>ark:/\d+/\w+)', view_collection_record, name='collectionrecord_view'),
    url(r'^(?P<ark>ark:/\d+/\w+)/', view_collection_record, name='collectionrecord_view'),
    )
