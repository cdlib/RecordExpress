from django.contrib import admin
import django.forms as forms
from django.contrib.contenttypes import generic
from DublinCore.models import QualifiedDublinCoreElement
from collection_record.models import CollectionRecord
from collection_record.models import SupplementalFile

class QDCElementInlineForm(forms.ModelForm):
    class Meta:
        model = QualifiedDublinCoreElement
    def __init__(self, *args, **kwargs):
        super(QDCElementInlineForm, self).__init__(*args, **kwargs)
        self.fields['term'] = forms.ChoiceField(choices=(('-','------'),)+QualifiedDublinCoreElement.DCELEMENTS)

class QDCElementInline(generic.GenericTabularInline):
    model = QualifiedDublinCoreElement
    extra = 0
    form = QDCElementInlineForm

class SupplementalFileInline(admin.TabularInline):
    model = SupplementalFile
    readonly_fields = ('filename',)
    extra = 0
    
def publish_to_oac(modeladmin, request, queryset):
    for collection in queryset.all():
        collection.save_ead_file()

class CollectionRecordAdmin(admin.ModelAdmin):
    #readonly_fields = ('ark', ) #Had to remove to allow adding through admin
    # still guarded in the CollectionRecord.save() method
    search_fields = ('ark', 'title', 'title_filing', 'abstract')
    list_display = ('ark', 'title_filing' , 'publisher', 'has_extended_metadata', 'has_supplemental_files', 'updated_at', 'created_at', )
    #list_filter = ('QDCElements',)
    inlines = (QDCElementInline, SupplementalFileInline)
    save_on_top = True
    actions = [publish_to_oac]

admin.site.register(CollectionRecord, CollectionRecordAdmin)
