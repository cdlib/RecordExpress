from string import Template
import os
import re
from xml.sax.saxutils import quoteattr
from xml.sax.saxutils import escape
from django.db import models
from django.contrib.contenttypes import generic
from django.conf import settings
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.template import Context

from ISO_639_2b import ISO_639_2b
from DublinCore.models import QualifiedDublinCoreElement

EAD_ROOT_DIR = settings.EAD_ROOT_DIR  if hasattr(settings, 'EAD_ROOT_DIR') else os.path.join(os.environ.get('HOME', '/dsc'), 'data/in/oac-ead/prime2002')

NOT_OAC = True
try:
    from oac.models import Institution
    NOT_OAC = False
except ImportError:
    pass

if NOT_OAC:
    class PublishingInstitution(models.Model):
        '''Publisher if you're not oac
        '''
        name = models.CharField(max_length=255)
        mainagency = models.CharField(max_length=255,)
        ark = models.CharField(max_length=255, unique=true)
        cdlpath = models.CharField(max_length=255, blank=True)


else:
    class PublishingInstitution(Institution):
        '''Proxy for the Institution, to make it look like a Publisher?
        '''
        class Meta:
            proxy = True

def dir_pairtree_for_ark(ark):
    '''Get our OAC pairtree like path for a given ark'''
    match = re.compile("ark:/(?P<NAAN>\d{5}|\d{9})/([a-zA-Z0-9=#\*\+@_\$/%-\.]+)$").match(ark)
    return os.path.join(match.group('NAAN'), ark[-2:], match.group(2), )


class CollectionRecord(models.Model):
    ark = models.CharField(max_length=255, primary_key=True)
    publisher = models.ForeignKey(PublishingInstitution)
    title = models.CharField(max_length=512,)
    title_filing = models.CharField(max_length=255)#, unique=True)
    date_dacs = models.CharField(max_length=128,)
    date_iso = models.CharField(max_length=128, blank=True)
    local_identifier = models.CharField(max_length=255, )
    extent=models.CharField(max_length=255)
    abstract=models.TextField()
    language = models.CharField(max_length=3, choices=(ISO_639_2b), help_text='Language of materials')
    accessrestrict = models.TextField()
    userestrict = models.TextField()
    acqinfo = models.TextField()
    scopecontent = models.TextField()
    bioghist = models.TextField(null=True, blank=True)
    online_items_url = models.URLField(null=True, blank=True, )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    QDCElements = generic.GenericRelation(QualifiedDublinCoreElement)

    class Meta:
        unique_together = (("title_filing", "publisher"), ("local_identifier",
            "publisher"))

    def __unicode__(self):
        return mark_safe(unicode(self.ark + ' : ' + self.title_filing))

    @models.permalink
    def get_absolute_url(self):
        return ('collectionrecord_view', (), {'ark': self.ark, })

    @models.permalink
    def get_edit_url(self):
        return ('collectionrecord_edit', (), {'ark': self.ark, })

    @property
    def ead_dir(self, directory_root=EAD_ROOT_DIR):
        return  os.path.join(directory_root, self.publisher.cdlpath)

    def save_ead_file(self, directory_root=EAD_ROOT_DIR):
        '''Save the EAD file to it's DSC CDL specific location?
        '''
        fname = os.path.join(self.ead_dir, self.ark.rsplit('/', 1)[1]+'.xml')
        with open(fname, 'w') as foo:
            foo.write(self.ead_xml)

    def save(self, *args, **kwargs):
        '''On save if ark is not set, get a new one from EZID.
        Also, if someone is trying to change the ARK, don't let them
        '''
        if self.pk:# existing object
            try:
                db_self = CollectionRecord.objects.get(pk=self.pk)
                if self.ark != db_self.ark:
                    #NOTE: this only works if I have a hidden numeric pk
                    raise ValueError('Can not change ARK for an collection')
            except CollectionRecord.DoesNotExist:
                pass
        if not self.ark:
            raise ValueError('Collection Records must have an ARK')
        super(CollectionRecord, self).save(*args, **kwargs)
        #TODO: save the ead file?? can use a public bool to determine if saved 
        # to disk
        self.save_ead_file()

    def has_extended_metadata(self):
        '''Tests if any extended metadata items (held in QDCElements)
        are associated with the instance.
        '''
        return True if self.QDCElements.count() > 0 else False
    has_extended_metadata.short_description = 'XMetadata'

    @property
    def has_supplemental_files(self):
        return self.supplementalfile_set.count() > 0

    @property
    def dir_supplemental_files(self):
        root_dir = os.environ.get('XTF_DATA', '/dsc/data/xtf/data')
        j
        dir_supp_files = os.path.join(root_dir, dir_pairtree_for_ark(self.ark), 'files')
        return dir_supp_files 

    #or should I just make a nice dictionary of subsetted values?
    #Need to define corresponding accessors (& setters?) for the various
    #multi-valued terms stored in the QDCElements.
    @property
    def creator_person(self):
        return self.QDCElements.all().filter(term__exact='CR').filter(qualifier__exact='person')

    @property
    def creator_family(self):
        return self.QDCElements.all().filter(term__exact='CR').filter(qualifier__exact='family')

    @property
    def creator_organization(self):
        return self.QDCElements.all().filter(term__exact='CR').filter(qualifier__exact='organization')

    @property
    def subject_topic(self):
        return self.QDCElements.all().filter(term__exact='SUB').filter(qualifier__exact='topic')

    @property
    def subject_name_person(self):
        return self.QDCElements.all().filter(term__exact='SUB').filter(qualifier__exact='name_person')

    @property
    def subject_name_family(self):
        return self.QDCElements.all().filter(term__exact='SUB').filter(qualifier__exact='name_family')

    @property
    def subject_name_organization(self):
        return self.QDCElements.all().filter(term__exact='SUB').filter(qualifier__exact='name_organization')

    @property
    def subject_title(self):
        return self.QDCElements.all().filter(term__exact='SUB').filter(qualifier__exact='title')

    @property
    def subject_function(self):
        return self.QDCElements.all().filter(term__exact='SUB').filter(qualifier__exact='function')

    @property
    def subject_occupation(self):
        return self.QDCElements.all().filter(term__exact='SUB').filter(qualifier__exact='occupation')

    @property
    def coverage(self):
        return self.QDCElements.all().filter(term__exact='CVR').filter(qualifier__exact='geo')

    @property
    def type_format(self):
        return self.QDCElements.all().filter(term__exact='TYP').filter(qualifier__exact='genre')

    @property
    def ead_xml(self):
        '''Return a unicode object that contains the EAD xml for the collection
        record
        '''
        ead_template = get_template('collection_record/collection_record/ead_template.xml')
        ead_template_data = dict( 
                    instance = self,
                    publisher_marc = quoteattr(self.publisher.mainagency),
                )
        c = Context(ead_template_data)
        ead_xml = ead_template.render(c)
        return ead_xml

class SupplementalFile(models.Model):
    '''A file associated with a Collection record'''
    collection_record = models.ForeignKey(CollectionRecord, editable=False)
    filename = models.CharField(max_length=78, blank=False, null=False, )#limited by unique key of ark(255 long) and this 1000 *byte* limit, 3byte unichar
    label = models.CharField(max_length=512, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def file_path(self):
        return os.path.join(self.collection_record.dir_supplemental_files, self.filename)

    @property
    def URL(self):
        '''Calculate the url path to the file'''
        ark_dir = dir_pairtree_for_ark(self.collection_record.ark)
        return "/data/"+ark_dir+'/files/'+self.filename

    @property
    def xml(self):
        '''Return the EAD xml representation for the file
        '''
        xml_label = escape(self.label) if self.label else escape(self.filename)
        return ''.join(('<item><extref href="', self.URL, '">', escape(self.URL), '</extref>', xml_label, '</item>'))

    class Meta:
        unique_together = (("filename", "collection_record"))

    def clean(self):
        super(SupplementalFile, self).clean()
        if not self.filename:
            raise ValidationError("Use the editing application to add files....")

    def delete(self, **kwargs):
        '''Delete the file first then the DB object'''
        os.remove(self.file_path)
        super(SupplementalFile, self).delete(**kwargs)

    def unicode(self):
        return ''.join((self.filename, ' for ', self.collection_record))
