from django.conf.urls.defaults import *

from collection_record.views import add_collection_record
from collection_record.views import view_collection_record
from collection_record.views import view_collection_record_xml
from collection_record.views import view_all_collection_records

urlpatterns = patterns('',
    url(r'^add', add_collection_record, name='collection_record_add'),
    url(r'^(?P<ark>ark:/\d+/\w+)$', view_collection_record, name='collectionrecord_view'),
    url(r'^(?P<ark>ark:/\d+/\w+)/$', view_collection_record, name='collectionrecord_view'),
    url(r'^(?P<ark>ark:/\d+/\w+)/xml/', view_collection_record_xml, name='collectionrecord_view_xml'),
    url(r'^|/$', view_all_collection_records, name='collection_record_view_all'),
)
