from string import Template
from django.db import models
from django.contrib.contenttypes import generic

from ISO_639_2b import ISO_639_2b
from DublinCore.models import QualifiedDublinCoreElement

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
        mainagency = models.CharField(max_length=255, null=True, blank=True)


else:
    class PublishingInstitution(Institution):
        '''Proxy for the Institution, to make it look like a Publisher?
        '''
        class Meta:
            proxy = True



class CollectionRecord(models.Model):
    ark = models.CharField(max_length=255, unique=True) #mysql length limit
    publisher = models.ForeignKey(PublishingInstitution)
    title = models.CharField(max_length=512,)
    title_filing = models.SlugField(max_length=255)#, unique=True)
    date_dacs = models.CharField(max_length=128,)
    date_iso = models.CharField(max_length=128,)
    local_identifier = models.CharField(max_length=255, )
    extent=models.CharField(max_length=255)
    abstract=models.TextField()
    language = models.CharField(max_length=3, choices=(ISO_639_2b))
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

    @models.permalink
    def get_absolute_url(self):
        return ('collectionrecord_view', (), {'ark': self.ark, })

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
        return super(CollectionRecord, self).save(*args, **kwargs)

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
        return self.QDCElements.all().filter(term__exact='COV').filter(qualifier__exact='geo')

    @property
    def type_format(self):
        return self.QDCElements.all().filter(term__exact='TYP').filter(qualifier__exact='genre')

    @property
    def ead_xml(self):
        '''Return a unicode object that contains the EAD xml for the collection
        record
        '''
        #should I add an xml output for all the various fields?
        #could be a big map/template thingy?
        ead_head_template_str = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ead PUBLIC "+//ISBN 1-931666-00-8//DTD ead.dtd (Encoded Archival Description (EAD) Version 2002)//EN" "ead.dtd">
<ead>
<eadheader langencoding="iso639-2b" scriptencoding="iso15924" repositoryencoding="iso15511" countryencoding="iso3166-1" dateencoding="iso8601">
<eadid countrycode="us" identifier="$ark" mainagencycode="${publisher_marc}">$local_identifier</eadid>
<filedesc>
<titlestmt>
<titleproper>$title</titleproper>
<titleproper type="filing">$title_filing</titleproper>
<author>${publisher_name}</author>
</titlestmt>
<publicationstmt>
<publisher>${publisher_name}</publisher>
<date>$date_dacs</date>
</publicationstmt>
</filedesc>
</eadheader>
<archdesc level="collection">
<did>
<head>Descriptive Summary</head>
<unittitle label="Title">$title</unittitle>
<unitdate normal="$date_iso" label="Dates"></unitdate>
<unitid label="Collection Number" repositorycode="${publisher_marc}" countrycode="US">$local_identifier</unitid>
'''
        collection_mapping = dict()
        for f in self._meta.fields:
            collection_mapping[f.name] = getattr(self, f.name)
        collection_mapping['publisher_marc'] = self.publisher.mainagency
        collection_mapping['publisher_name'] = self.publisher.name
        ead_head_template = Template(ead_head_template_str)
        ead_xml = ead_head_template.substitute(collection_mapping)
        origination_xml = '<origination label="Creator/Collector">\n'
        for qdc in self.creator_person:
            origination_xml = ''.join((origination_xml, '<persname>', qdc.content, '</persname>\n',))
        for qdc in self.creator_family:
            origination_xml = ''.join((origination_xml, '<famname>', qdc.content, '</famname>\n',))
        for qdc in self.creator_organization:
            origination_xml = ''.join((origination_xml, '<corpname>', qdc.content, '</corpname>\n',))
        origination_xml = ''.join((origination_xml, '</origination>\n',))
        ead_xml = ''.join((ead_xml, origination_xml,))
        ead_xml = ''.join((ead_xml, '<physdesc label="Extent"><extent>', self.extent, '</extent>\n',))
        if self.online_items_url:
            ead_xml = ''.join((ead_xml, '<extent type="dao">Online items available</extent>\n<dao role="http://oac.cdlib.org/arcrole/link/search/" href="', self.online_items_url, '" title="Online items"/>\n',))
        ead_xml = ''.join((ead_xml, '</physdesc>\n',))
        ead_xml = ''.join((ead_xml, '<repository label="Repository">\n<corpname>', self.publisher.name, '</corpname>\n</repository>\n'))
        ead_xml = ''.join((ead_xml, '<abstract label="Abstract">', self.abstract, '</abstract>\n',))
        ead_xml = ''.join((ead_xml, '<langmaterial><language langcode="', self.language, '"/></langmaterial>\n',))
        ead_xml = ''.join((ead_xml, '</did>\n', ))
        ead_xml = ''.join((ead_xml, '<accessrestrict><head>Access</head><p>', self.accessrestrict, '</p></accessrestrict>\n',))
        ead_xml = ''.join((ead_xml, '<userestrict><head>Publication Rights</head><p>', self.userestrict, '</p></userestrict>\n',))
        ead_xml = ''.join((ead_xml, '<prefercite><head>Preferred Citation</head><p>', self.title, ' , ',  self.local_identifier, '.  ', self.publisher.name, '.</p></prefercite>\n',))
        ead_xml = ''.join((ead_xml, '<acqinfo><head>Acquisition Information</head><p>', self.acqinfo, '</p></acqinfo>\n',))
        if self.bioghist:
            ead_xml = ''.join((ead_xml, '<bioghist><head>Biography/Administrative History</head><p>', self.bioghist, '</p></bioghist>',))
        ead_xml = ''.join((ead_xml, '<scopecontent><head>Scope and Content of Collection</head><p>', self.scopecontent, '</p></scopecontent>',))
        controlaccess_xml = '<controlaccess>\n<head>Indexing Terms</head>\n'
        for qdc in self.subject_topic:
            controlaccess_xml = ''.join((controlaccess_xml, '<subject>', qdc.content, '</subject>\n',))
        for qdc in self.subject_name_person:
            controlaccess_xml = ''.join((controlaccess_xml, '<persname role="subject">', qdc.content, '</persname>\n',))
        for qdc in self.subject_name_family:
            controlaccess_xml = ''.join((controlaccess_xml, '<famname role="subject">', qdc.content, '</famname>\n',))
        for qdc in self.subject_name_organization:
            controlaccess_xml = ''.join((controlaccess_xml, '<corpname role="subject">', qdc.content, '</corpname>\n',))
        for qdc in self.coverage:
            controlaccess_xml = ''.join((controlaccess_xml, '<geogname role="subject">', qdc.content, '</geogname>\n',))
        for qdc in self.type_format:
            controlaccess_xml = ''.join((controlaccess_xml, '<genreform role="subject">', qdc.content, '</genreform>\n',))
        for qdc in self.subject_title:
            controlaccess_xml = ''.join((controlaccess_xml, '<title role="subject">', qdc.content, '</title>\n',))
        for qdc in self.subject_function:
            controlaccess_xml = ''.join((controlaccess_xml, '<function role="subject">', qdc.content, '</function>\n',))
        for qdc in self.subject_occupation:
            controlaccess_xml = ''.join((controlaccess_xml, '<occupation role="subject">', qdc.content, '</occupation>\n',))
        controlaccess_xml = ''.join((controlaccess_xml, '</controlaccess>\n',))
        ead_xml = ''.join((ead_xml, controlaccess_xml))
        ead_xml = ''.join((ead_xml, '</archdesc>\n</ead>\n',))
        return ead_xml
