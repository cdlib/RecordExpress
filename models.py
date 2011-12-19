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
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    QDCElements = generic.GenericRelation(QualifiedDublinCoreElement)

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
