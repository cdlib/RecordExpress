from django.db import models
from django.contrib.contenttypes import generic

from ISO_639_2b import ISO_639_2b
from DublinCore.models import QualifiedDublinCoreElement

class CollectionRecord(models.Model):
    ark = models.CharField(max_length=255, unique=True) #mysql length limit
    title = models.CharField(max_length=512,)
    title_filing = models.SlugField(max_length=255, unique=True)
    date_dacs = models.CharField(max_length=128,)
    date_iso = models.CharField(max_length=128,)
    local_identifier = models.CharField(max_length=512, )
    extent=models.CharField(max_length=255)
    abstract=models.TextField()
    language = models.CharField(max_length=3, choices=(ISO_639_2b))
    accessrestrict = models.TextField()
    userestrict = models.TextField()
    acqinfo = models.TextField()
    scopecontent = models.TextField()
    bioghist = models.TextField(null=True, blank=True)
    online_items_url = models.URLField(null=True, blank=True, )
    QDCElements = generic.GenericRelation(QualifiedDublinCoreElement)

    #or should I just make a nice dictionary of subsetted values?
    #Need to define corresponding accessors (& setters?) for the various
    #multi-valued terms stored in the QDCElements.
    @property
    def creator_person(self):
        #return a subsetted QDCElements
        return QDCElements.all().filter(term__exact='CR').filter(qualifier_exact='person')

    @property
    def creator_family(self):
        #return a subsetted QDCElements
        return QDCElements.all().filter(term__exact='CR').filter(qualifier_exact='family')

    @property
    def creator_organization(self):
        #return a subsetted QDCElements
        return QDCElements.all().filter(term__exact='CR').filter(qualifier_exact='organization')

    @property
    def subject_topic(self):
        #return a subsetted QDCElements
        return QDCElements.all().filter(term__exact='SUB').filter(qualifier_exact='topic')

    @property
    def subject_name_person(self):
        #return a subsetted QDCElements
        return QDCElements.all().filter(term__exact='SUB').filter(qualifier_exact='name_person')

    @property
    def subject_name_family(self):
        #return a subsetted QDCElements
        return QDCElements.all().filter(term__exact='SUB').filter(qualifier_exact='name_family')

    @property
    def subject_name_organization(self):
        #return a subsetted QDCElements
        return QDCElements.all().filter(term__exact='SUB').filter(qualifier_exact='name_organization')

    @property
    def subject_title(self):
        #return a subsetted QDCElements
        return QDCElements.all().filter(term__exact='SUB').filter(qualifier_exact='title')

    @property
    def subject_function(self):
        #return a subsetted QDCElements
        return QDCElements.all().filter(term__exact='SUB').filter(qualifier_exact='function')

    @property
    def subject_occupation(self):
        #return a subsetted QDCElements
        return QDCElements.all().filter(term__exact='SUB').filter(qualifier_exact='occupation')

    @property
    def coverage(self):
        return QDCElements.all().filter(term__exact='COV').filter(qualifier_exact='geo')

    @property
    def type(self):
        #return a subsetted QDCElements
        return QDCElements.all().filter(term__exact='TYP').filter(qualifier_exact='genre')
