# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'CollectionRecord.updated_at'
        db.add_column('collection_record_collectionrecord', 'updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2011, 12, 19, 17, 27, 55, 486755), blank=True), keep_default=False)

        # Adding field 'CollectionRecord.created_at'
        db.add_column('collection_record_collectionrecord', 'created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2011, 12, 19, 17, 28, 3, 966766), blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'CollectionRecord.updated_at'
        db.delete_column('collection_record_collectionrecord', 'updated_at')

        # Deleting field 'CollectionRecord.created_at'
        db.delete_column('collection_record_collectionrecord', 'created_at')


    models = {
        'dublincore.qualifieddublincoreelement': {
            'Meta': {'ordering': "['term']", 'object_name': 'QualifiedDublinCoreElement'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'qualifier': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'collection_record.collectionrecord': {
            'Meta': {'object_name': 'CollectionRecord'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'accessrestrict': ('django.db.models.fields.TextField', [], {}),
            'acqinfo': ('django.db.models.fields.TextField', [], {}),
            'ark': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'bioghist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_dacs': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'date_iso': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'extent': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'local_identifier': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'online_items_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'scopecontent': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'title_filing': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'userestrict': ('django.db.models.fields.TextField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['collection_record']
