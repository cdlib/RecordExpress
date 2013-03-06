from django.conf.urls.defaults import *

from collection_record.views import add_collection_record
from collection_record.views import edit_collection_record
from collection_record.views import view_collection_record_xml
from collection_record.views import view_all_collection_records
from collection_record.views import view_collection_record_oac_preview

urlpatterns = patterns('',
    url(r'^add/', add_collection_record, name='collection_record_add'),
    url(r'^(?P<ark>ark:/\d+/\w+)/$', view_collection_record_oac_preview, name='collectionrecord_view'),
    url(r'^(?P<ark>ark:/\d+/\w+)/xml/$', view_collection_record_xml, name='collectionrecord_view_xml'),
    url(r'^(?P<ark>ark:/\d+/\w+)/oac/$', view_collection_record_oac_preview, name='collectionrecord_view_oac'),
    url(r'^(?P<ark>ark:/\d+/\w+)/edit/$', edit_collection_record, name='collectionrecord_edit'),
    url(r'^(?P<pk>\d+)/$', view_collection_record_oac_preview, name='collectionrecord_view'),
    url(r'^(?P<pk>\d+)/xml/$', view_collection_record_xml, name='collectionrecord_view_xml'),
    url(r'^(?P<pk>\d+)/oac/$', view_collection_record_oac_preview, name='collectionrecord_view_oac'),
    url(r'^(?P<pk>\d+)/edit/$', edit_collection_record, name='collectionrecord_edit'),
    url(r'^/$', view_all_collection_records, name='collection_record_view_all'),
    url(r'^$', view_all_collection_records, name='collection_record_view_all'),#NOTE: when "included" the / winds up as an empty path in here
)
