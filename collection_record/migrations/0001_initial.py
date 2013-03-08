# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CollectionRecord'
        db.create_table('collection_record_collectionrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ark', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('title_filing', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255, db_index=True)),
            ('date_dacs', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('date_iso', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('local_identifier', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('extent', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('accessrestrict', self.gf('django.db.models.fields.TextField')()),
            ('userestrict', self.gf('django.db.models.fields.TextField')()),
            ('acqinfo', self.gf('django.db.models.fields.TextField')()),
            ('scopecontent', self.gf('django.db.models.fields.TextField')()),
            ('bioghist', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('online_items_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('collection_record', ['CollectionRecord'])


    def backwards(self, orm):
        
        # Deleting model 'CollectionRecord'
        db.delete_table('collection_record_collectionrecord')


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
