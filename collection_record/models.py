from string import Template
import logging
import os
import re
from xml.sax.saxutils import quoteattr
from xml.sax.saxutils import escape
import codecs
import subprocess
import shlex
import datetime
from django.db import models
from django.contrib.contenttypes import generic
from django.conf import settings
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.template import Context
from is_oac import is_OAC
from ISO_639_2b import ISO_639_2b
from dublincore.models import QualifiedDublinCoreElement

logger = logging.getLogger(__name__)

OAC = is_OAC()
if not OAC:
    class PublishingInstitution(models.Model):
        '''Publisher if you're not oac
        '''
        name = models.CharField(max_length=255)
        mainagency = models.CharField(max_length=255,)
        ark = models.CharField(max_length=255, blank=True)
        cdlpath = models.CharField(max_length=255, blank=True)
        parent_institution = models.ForeignKey('self', null=True, blank=True, related_name='children')
        def __unicode__(self):
            return self.name
else:
    from oac.models import Institution
    class PublishingInstitution(Institution):
        '''Proxy for the Institution, to make it look like a Publisher?
        '''
        class Meta:
            proxy = True

def dir_pairtree_for_ark(ark):
    '''Get our OAC pairtree like path for a given ark'''
    match = re.compile("ark:/(?P<NAAN>\d{5}|\d{9})/([a-zA-Z0-9=#\*\+@_\$/%-\.]+)$").match(ark)
    return os.path.join(match.group('NAAN'), ark[-2:], match.group(2), )

def rightpart_for_ark(ark):
    match = re.compile("ark:/(?P<NAAN>\d{5}|\d{9})/([a-zA-Z0-9=#\*\+@_\$/%-\.]+)$").match(ark)
    return match.group(2)


class CollectionRecord(models.Model):
    #TODO: remove EZID minter and ARK_validator.
    ark = models.CharField(max_length=255, primary_key=True)
    publisher = models.ForeignKey(PublishingInstitution, verbose_name='Publishing Institution')
    title = models.CharField('Collection Title', max_length=512,)
    title_filing = models.CharField('Collection Title (Filing)', max_length=255)
    local_identifier = models.CharField('Collection Identifier/Call Number', max_length=255, )
    date_dacs = models.CharField('Collection Date', max_length=128,)
    date_iso = models.CharField('Collection Date (ISO 8601 Format)', help_text='Enter the dates normalized using the ISO 8601 format', max_length=128, blank=True)
    extent=models.CharField('Extent of Collection', max_length=1000)
    abstract=models.TextField()
    language = models.CharField('Language of materials', max_length=3, choices=(ISO_639_2b), )
    accessrestrict = models.TextField('Access Conditions')
    userestrict = models.TextField('Publication Rights', blank=True)
    acqinfo = models.TextField('Acquisition Information', blank=True)
    scopecontent = models.TextField('Scope and Content of Collection')
    bioghist = models.TextField('Biography/Administrative History', null=True, blank=True)
    online_items_url = models.URLField('Online Items URL', null=True, blank=True, )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    QDCElements = generic.GenericRelation(QualifiedDublinCoreElement)

    class Meta:
        unique_together = (
                ("title_filing", "publisher")
                )

    def __unicode__(self):
        return mark_safe(unicode(self.ark + ' : ' + self.title_filing))

    def __unicode__(self):
        return mark_safe(unicode(self.ark + ' : ' + self.title_filing))

    @models.permalink
    def get_absolute_url(self):
        return ('collectionrecord_view', (), {'ark': self.ark, })

    @models.permalink
    def get_edit_url(self):
        return ('collectionrecord_edit', (), {'ark': self.ark, })

    @models.permalink
    def get_xml_url(self):
        return ('collectionrecord_view_xml', (), {'ark': self.ark, })

    def _get_dir_root(self):
        if hasattr(self, '_dir_root'):
            return self._dir_root
        else:
            EAD_ROOT_DIR='./data-ead/'
            if os.path.exists('~/.recordexpressrc'):
                #TODO: get root from config
                pass
            else:
                if os.environ.has_key('EAD_ROOT_DIR'):
                    EAD_ROOT_DIR = os.environ.get('EAD_ROOT_DIR')
                else:
                    try:
                        EAD_ROOT_DIR = settings.EAD_ROOT_DIR
                    except AttributeError:
                        pass
                    if OAC and EAD_ROOT_DIR == './data-ead/':
                        EAD_ROOT_DIR = os.path.join(os.environ.get('HOME', '/apps/dsc'), 'data/in/oac-ead/prime2002')
            self._dir_root = EAD_ROOT_DIR
            return EAD_ROOT_DIR

    def _set_dir_root(self, value):
        self._dir_root = value
    dir_root = property(_get_dir_root, _set_dir_root)

    def _get_xtf_dir_root(self):
        if hasattr(self, '_xtf_dir_root'):
            return self._xtf_dir_root
        else:
            XTF_DATA=None
            if os.environ.has_key('XTF_DATA'):
                XTF_DATA = os.environ.get('XTF_DATA')
            else:
                try:
                    XTF_DATA = settings.XTF_ROOT_DIR
                except AttributeError:
                    pass
                if not XTF_DATA:
                    XTF_DATA = os.path.join(os.environ.get('HOME', '/apps/dsc'), 'data/xtf/data')
            if not XTF_DATA:
                XTF_DATA = './data'
            return XTF_DATA

    def _set_xtf_dir_root(self, value):
        self._xtf_dir_root = value
    xtf_dir_root = property(_get_xtf_dir_root, _set_xtf_dir_root)

    @property
    def ead_dir(self):
        return  os.path.join(self.dir_root, self.publisher.cdlpath)

    @property
    def ead_filename(self):
        if OAC:
            fname = os.path.join(self.ead_dir, self.ark.rsplit('/', 1)[1]+'.xml')
        else:
            fname = os.path.join(self.ead_dir, self.title_filing.replace(' ', '_')+'.xml')
        return fname

    @property
    def has_xtf_mets(self):
        # /dsc/data/xtf//data/13030/qb/c8f47vqb/c8f47vqb.mets.xml
        file_to_test = os.path.join(self.xtf_dir_root,
                                    dir_pairtree_for_ark(self.ark),
                                    '{0}.mets.xml'.format(rightpart_for_ark(self.ark)))
        return os.path.isfile(file_to_test)

    def delete(self, **kwargs):
        '''Run holdMets.pl on the ark, then
        delete the file first then the DB object'''
        if OAC and self.has_xtf_mets:
            HOME_DIR = os.environ.get('HOME', '/apps/dsc/')
            holdMets_path = os.path.join( HOME_DIR,
                                    'branches/production/voro/batch-bin/holdMETS.pl')
            #setup log file
            log_path = os.path.join(HOME_DIR, 'log/holdMets/', self.ark.replace(':','').replace('/', '-'))
            with open(log_path, 'w') as logfile: 
                logfile.write('Running:'+holdMets_path+' '+self.ark)
                returncode = subprocess.call((holdMets_path, self.ark),
                                stdout=logfile,
                                stderr=subprocess.STDOUT
                                )
                if returncode != 0 and returncode != 103:
                    raise Exception('Error with holdMets removal process. Check log:'+log_path)
        if os.path.isfile(self.ead_filename):
            os.remove(self.ead_filename)
        super(CollectionRecord, self).delete(**kwargs)

    def save_ead_file(self):
        '''Save the EAD file to it's DSC CDL specific location?
        '''
        if not os.path.exists(self.ead_dir):
            os.makedirs(self.ead_dir)
        fname = self.ead_filename
        fdir, fname = os.path.split(fname)
        fname = fname[:139]
        olddir = os.getcwd()
        os.chdir(fdir)
        foo =  codecs.open(fname, 'w', 'utf-8')
        try:
            foo.write(self.ead_xml)
            foo.close()
        except:
            foo.close()
            #cleanup if necessary
            try:
                if os.path.isfile(self.ead_filename):
                    os.remove(fname) #TODO: TEST THIS
            except:
                print "!!!! PROBLEM REMOVING %s. Check that its gone !!!" % (fname, )
        os.chdir(olddir)

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
        if OAC:
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
        #TODO: make not OAC ARK specific, but allow when OAC
        return os.path.join(self.xtf_dir_root, dir_pairtree_for_ark(self.ark), 'files')

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
        self.publisher.name_leaf_inst = self.publisher.name
        if self.publisher.parent_institution:
            #DACS 14.13
            self.publisher.name =  "{0}. {1}".format(self.publisher.parent_institution.name, self.publisher.name)
        ead_template_data = dict( 
                    instance = self,
                    publisher_marc = quoteattr(self.publisher.mainagency),
                    publishing_year = datetime.date.today().year
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
    def txt_file_path(self):
        '''Return path to the ripped txt file'''
        return  ''.join((unicode(self.file_path)[:-4], '.txt'))

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
        return ''.join(('<item><extref href=', quoteattr(self.URL), '>', xml_label, '</extref></item>'))

    class Meta:
        unique_together = (("filename", "collection_record"))

    def clean(self):
        super(SupplementalFile, self).clean()
        if not self.filename:
            raise ValidationError("Use the editing application to add files....")
        (name, ext) = os.path.splitext(self.filename)
        if ext != '.pdf':
            raise ValidationError("Only PDF files can be uploaded as supplemental documents")
        self.filename = self.filename

    def get_filehandle(self, mode):
        '''Return an open filehandle to the underlying file system object'''
        if not mode:
            mode = 'wb'
        if not os.path.isdir(self.collection_record.dir_supplemental_files):
            os.makedirs(self.collection_record.dir_supplemental_files)
        return  open(os.path.join(self.collection_record.dir_supplemental_files, unicode(self.filename)), mode)

    def rip_to_text(self):
        '''Rip pdf to text, place next to pdf file'''
        pdftotext_command = "java -jar " + os.environ['HOME'] + "/java/pdfbox/pdfbox-app.jar ExtractText -force"
        out_file_path = os.path.splitext(self.file_path)[0] + '.txt'

        cmd_line = ''.join((pdftotext_command, ' "', str(self.file_path), '" "', str(out_file_path), '"'))
        args = shlex.split(cmd_line)
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        p.wait()
        if p.returncode:
            stdout = p.stdout.read()
            stderr = p.stderr.read()
            logger.error("Problem ripping %s to text: %s" % (self.file_path, stderr))
            raise Exception("Problem ripping %s to text: %s" % (self.file_path, stderr))
        # perl -pi -e 's/[[:cntrl:]]/ /g'
        fix_illegal_in_xml_command = "perl -pi -e 's/[[:cntrl:]]/ /g' "
        args2 = shlex.split(fix_illegal_in_xml_command ) + [out_file_path]
        p = subprocess.Popen(args2, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        p.wait()
        if p.returncode:
            stdout = p.stdout.read()
            stderr = p.stderr.read()
            logger.error("Problem cleaning illegal characters %s: %s" % (self.file_path, stderr))
            raise Exception("Problem cleaning illegal characters %s: %s" % (self.file_path, stderr))

    
    def delete(self, **kwargs):
        '''Delete the file first then the DB object'''
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)
        (fpath, ext) = os.path.splitext(self.file_path)
        if os.path.isfile(self.txt_file_path):
            os.remove(self.txt_file_path)
        super(SupplementalFile, self).delete(**kwargs)
        self.collection_record.save_ead_file() # to force re-indexing

    def unicode(self):
        return ''.join((self.filename, ' for ', self.collection_record))
