import os
import sys
from urllib import quote
import xml.etree.ElementTree as ET
import shutil
import glob
from django.conf import settings
from django.test import TestCase
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.db.models.base import ValidationError
from django.contrib.auth.models import User
from django_webtest import WebTest
from collection_record.forms import CollectionRecordForm
from collection_record.models import CollectionRecord
from collection_record.models import SupplementalFile
from collection_record.perm_backend import CollectionRecordPermissionBackend
from collection_record.perm_backend import get_publishing_institutions_for_user

debug_print = lambda x: sys.stdout.write(x+'\n\n') if os.environ.get('DEBUG', False) else lambda x: x

class CollectionRecordTestDirSetupMixin(object):
    '''Mixin to add override of output directory for EAD files'''
    dir_root = os.path.join(os.path.abspath(os.path.split(__file__)[0]), 'data')

    def setUp(self):
        '''Override the "databases" config file to use the test shoulder'''
##        os.environ['DATABASES_XML_FILE'] = os.path.join(os.environ['HOME'], '.databases-test.xml')
        os.environ['EAD_ROOT_DIR'] = CollectionRecordTestDirSetupMixin.dir_root
        if not os.path.isdir(CollectionRecordTestDirSetupMixin.dir_root):
            os.makedirs(CollectionRecordTestDirSetupMixin.dir_root)
        debug_print( "TEST DIR ROOT==========>" + CollectionRecordTestDirSetupMixin.dir_root)
        super(CollectionRecordTestDirSetupMixin, self).setUp()

    def tearDown(self):
        debug_print("DELETING TEST DIR------------>" + CollectionRecordTestDirSetupMixin.dir_root)
        if os.path.isdir(CollectionRecordTestDirSetupMixin.dir_root):
            shutil.rmtree(CollectionRecordTestDirSetupMixin.dir_root)
        super(CollectionRecordTestDirSetupMixin, self).tearDown()


class CollectionRecordModelTest(CollectionRecordTestDirSetupMixin, TestCase):
    '''Test the CollectionRecord django model'''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'collection_record.supplementalfile.json', 'collection_record.publishinginstitution.json', 'collection_record.auth.user.json']

    def testModelExists(self):
        rec = CollectionRecord()
        self.failUnlessRaises(ValidationError, rec.full_clean)

    def testEZID_DublinCoreUpdate(self):
        '''Test that the Dublin Core attrs of the EZID get updateed by 
        a save of the object.
        '''
        pass

    def testEAD_xml_output(self):
        '''Test the ead string output for a CollectionRecord. Check unicode
        support
        '''
        rec = CollectionRecord.objects.get(pk="1")
        ead_xml = rec.ead_xml
        self.failUnless(ead_xml.index('<?xml') == 0)
        self.failUnless('<ead>' in ead_xml)
        self.failUnless('1' in ead_xml)
        self.failUnless('persname' in ead_xml)
        self.failUnless('<physdesc label="Extent">' in ead_xml)
        self.failUnless('<repository label="' in ead_xml)
        self.failUnless('<abstract label="Abstract">' in ead_xml)
        self.failUnless('<langmaterial><language langcode="' in ead_xml)
        self.failUnless('<accessrestrict id="accessrestrict"><head>Access</head><p>' in ead_xml)
        self.failUnless('<userestrict id="userestrict"><head>Publication Rights</head><p>' in ead_xml)
        self.failUnless('<prefercite id="prefercite"><head>Preferred Citation</head>' in ead_xml)
        self.failUnless('<acqinfo id="acqinfo"><head>Acquisition Information</head>' in ead_xml)
        self.failUnless('<bioghist id="bioghist"><head>Biography/Administrative History</head>' in ead_xml)
        self.failUnless('<scopecontent id="scopecontent"><head>Scope and Content of Collection</head>' in ead_xml)
        self.failUnless('<controlaccess id="controlaccess">' in ead_xml)
        self.failUnless('id="archdesc' in ead_xml)
        self.failUnless('</archdesc>' in ead_xml)
        self.failUnless('</ead>' in ead_xml)
        self.failUnless('repositorycode="'+rec.publisher.mainagency+'" countrycode="US">'+rec.local_identifier+'</unitid>' in ead_xml)
        self.failIf('<!DOCTYPE' in ead_xml)
        self.failUnless('UC' in ead_xml)
        try:
            etree = ET.XML(ead_xml.encode('utf-8'))
        except:
            import sys
            print sys.exc_info()
            self.fail('ElementTree could not parse xml')
        archdesc = etree.find('archdesc')
        did = archdesc.find('did')
        corpname = did.find('repository/corpname')
        self.failUnless('UC' in corpname.text)
        prefercite_p = archdesc.find('prefercite/p')
        self.failUnless('UC' in prefercite_p.text)
        unitdate = did.find('unitdate')
        self.failIf(unitdate.text is None)

    def testEAD_iso_date(self):
        '''Check that the unitdate "normal" attribute only shows up for 
        records with date_iso
        '''
        rec = CollectionRecord.objects.get(pk="2")
        ead_xml = rec.ead_xml
        try:
            etree = ET.XML(ead_xml.encode('utf-8'))
        except:
            import sys
            print sys.exc_info()
            self.fail('ElementTree could not parse xml')
        archdesc = etree.find('archdesc')
        did = archdesc.find('did')
        unitdate = did.find('unitdate')
        self.failIf(unitdate.text is None)
        self.failIf('normal' in unitdate.attrib)
        rec = CollectionRecord.objects.get(pk="1")
        ead_xml = rec.ead_xml
        try:
            etree = ET.XML(ead_xml.encode('utf-8'))
        except:
            import sys
            print sys.exc_info()
            self.fail('ElementTree could not parse xml')
        archdesc = etree.find('archdesc')
        did = archdesc.find('did')
        unitdate = did.find('unitdate')
        self.failIf(unitdate.text is None)
        self.failUnless('normal' in unitdate.attrib)

    def testEAD_xml_with_files_output(self):
        rec = CollectionRecord.objects.get(pk="4")
        ead_xml = rec.ead_xml
        try:
            ET.fromstring(ead_xml)
        except:
            self.fail('ElementTree could not parse xml')
        self.failUnless('</archdesc>' in ead_xml)
        self.failUnless('<otherfindaid' in ead_xml)
        self.failUnless('</extref>' in ead_xml)
        self.failUnless('test-2.pdf' in ead_xml)

    def testEAD_file_save(self):
        rec = CollectionRecord.objects.get(pk="1")
        dir_root = os.path.join(os.path.abspath(os.path.split(__file__)[0]), 'data')
        rec.dir_root = dir_root
        if not os.path.isdir(rec.ead_dir):
            os.makedirs(rec.ead_dir)
        rec.save_ead_file()
        if not os.path.exists(rec.ead_filename):
            self.fail('Did not create EAD file %s' %(rec.ead_filename,))

    def testXMLURL(self):
        '''test that the xml url function exists & returns something.
        '''
        rec = CollectionRecord.objects.get(pk="4")
        url = rec.get_xml_url
        self.failUnless(url is not None)

    def testEAD_file_remove_on_delete(self):
        '''Test that the EAD xml file is removed when the Collection Record is 
        deleted
        '''
        rec = CollectionRecord.objects.get(pk="1")
        dir_root = os.path.join(os.path.abspath(os.path.split(__file__)[0]), 'data')
        rec.dir_root = dir_root
        if not os.path.isdir(rec.ead_dir):
            os.makedirs(rec.ead_dir)
        rec.save_ead_file()
        ead_fname = rec.ead_filename
        rec.delete()
        if os.path.exists(ead_fname):
            self.fail('Did not delete ead file %s' % (ead_fname,))


class CollectionRecordFormTestCase(CollectionRecordTestDirSetupMixin, TestCase):
    '''Test the form for creating new collection records. Is this form different
    from the existing record form?
    '''
    def testNewForm(self):
        f = CollectionRecordForm()
     

class CollectionRecordViewAllTestCase(CollectionRecordTestDirSetupMixin, TestCase):
    '''Test the view of all collection records for a a user
    '''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'collection_record.publishinginstitution.json', 'collection_record.auth.user.json']

#####    def setUp(self):
#####        super(CollectionRecordViewAllTestCase, self).setUp()
#####
    def testViewAllCollectionRecords(self):
        '''Verify that the user can see their institution's collection records
        and not others.
        '''
        url = reverse('collection_record_view_all', args=None)
        ret = self.client.login(username='testuser',password='testuser')
        response = self.client.get(url)
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'Collection')
        self.assertContains(response, '/collection-record/')
        ret = self.client.login(username='admin', password='admin')
        self.failUnless(ret)
        response = self.client.get(url)
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'Collection')
        self.assertContains(response, '5')
        self.assertContains(response, '/collection-record/')
        
    def testLinksOnCollectionRecordListPage(self):
        '''Check that some links do exist on the collection record list page
        '''
        url = reverse('collection_record_view_all', args=None)
        ret = self.client.login(username='testuser',password='testuser')
        response = self.client.get(url)
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, '/collection-record/')
        url_add = reverse('collection_record_add', args=None)
        self.assertContains(response, url_add)
        rec = CollectionRecord.objects.get(pk='2')
        url_rec = rec.get_absolute_url()
        self.assertContains(response, url_rec)
        url_xml = rec.get_xml_url()
        self.assertContains(response, url_xml)

#TODO:this is going to require a live test server for xtf to talk to
###class CollectionRecordXMLViewTestCase(CollectionRecordTestDirSetupMixin, WebTest):
###    '''Test views of the CollectionRecord'''
###    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'collection_record.publishinginstitution.json', 'collection_record.auth.user.json']
###    def setUp(self):
###        super(CollectionRecordXMLViewTestCase, self).setUp()
###
###
###    def testXMLView(self):
###        rec = CollectionRecord.objects.get(pk="1")
###        url = rec.get_absolute_url() + '/xml/'
###        ret = self.client.login(username='testuser',password='testuser')
###        response = self.client.get(url)
###        self.failUnlessEqual(200, response.status_code)
###        self.assertContains(response, '<ead>')
###        self.assertContains(response, 'Banc')


class CollectionRecordEditTestCase(CollectionRecordTestDirSetupMixin, WebTest, LiveServerTestCase):
    '''Test the edit page for the collection records. Should be able to modify
    all data (main & assoc. DCs) and delete and add DC stored data
    '''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'collection_record.publishinginstitution.json', 'collection_record.auth.user.json']
#    fixtures = ['collectionrecord.json', 'dublincore.json', 'publishinginstitution.json', 'auth.user.json']

    csrf_checks = False

    def setUp(self):
        super(CollectionRecordEditTestCase, self).setUp()
        rec = CollectionRecord.objects.get(pk="1")
        if not os.path.isdir(rec.ead_dir):
            os.makedirs(rec.ead_dir)

    def testEditPageAuth(self):
        rec = CollectionRecord.objects.get(pk="1")
        url = rec.get_edit_url()
        response = self.app.get(url)
        self.failUnlessEqual('302 FOUND', response.status)
        self.failUnlessEqual(302, response.status_code)
        self.assertTrue(settings.LOGIN_URL+'?next='+quote(url), response.headers['location'])
        response = self.app.get(url, user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'itle')
        self.assertContains(response, '<option value="eng" selected="selected">English</option>')
        self.assertContains(response, 'access')
        self.assertContains(response, 'logout')

    def testEditAttr(self):
        '''Edit a directly associated value of the Record'''
        rec = CollectionRecord.objects.get(pk="4")
        if not os.path.isdir(rec.ead_dir):
            os.makedirs(rec.ead_dir)
        url = rec.get_edit_url()
        response = self.app.get(url, user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'logout')
        form = response.forms['main_form']
        #fill out basic info only,required fields only
        form['title'] = 'Test Title'
        form['title_filing'] = 'Test Filing Title'
        form['date_dacs'] = 'circa 1980'
        form['date_iso'] = '1980'
        form['local_identifier'] = 'LOCALID-test'
        form['extent'] = 'loads of boxes'
        form['abstract'] = 'a nice test collection'
        form['accessrestrict'] = 'public domain'
        form['userestrict'] = 'go craxy'
        form['acqinfo'] = 'by mark'
        form['scopecontent'] = 'test content'
        response = form.submit(user='testuser')
        self.failUnlessEqual(302, response.status_code)
        response.follow()
        self.assertTemplateUsed(response,'collection_record/collection_record/ead_template.xml') 
        response = self.app.get(url, user='testuser')
        self.assertContains(response, 'logout')
        form = response.forms['main_form']
        form['title'] = ''
        response = form.submit(user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertTemplateUsed(response,'collection_record/collection_record/edit.html') 
        self.assertContains(response, 'errorlist')

    def testEditDCTerm(self):
        '''Test the editing of a term stored in an associated DC object
        '''
        u = User.objects.get(username="testuser")
        rec = CollectionRecord.objects.get(pk="1")
        url = rec.get_edit_url()
        response = self.app.get(url, user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'logout')
        form = response.forms['main_form']
        newPerson = 'Mark Redar Test'
        form['person-0-content'] = newPerson
        response = form.submit(user='testuser')
        self.failUnlessEqual(302, response.status_code)
        #self.assertRedirects(response, rec.get_absolute_url())
        response.follow(user='testuser')
        self.assertTemplateUsed(response,'collection_record/collection_record/ead_template.xml') 
        #NOTE: Currently can't test the updated "view" of the object because
        # of the xtf interaction, it goes to live back server
        response = self.app.get(url, user='testuser')
        self.assertTrue(newPerson in response)
        self.assertContains(response, newPerson)
        self.assertContains(response, 'logout')
        response = self.app.get(url, user='testuser')
        form['person-0-content'] = ''
        response = form.submit(user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'errorlist')

    def testDeletionOfDCTerm(self):
        '''Test the deletion of a term'''
        pass

class NewCollectionRecordViewTestCase(CollectionRecordTestDirSetupMixin, WebTest):
    fixtures = ['collection_record.publishinginstitution.json', 'collection_record.auth.user.json']
    def setUp(self):
        testuser = User.objects.get(username='testuser')
        for i in get_publishing_institutions_for_user(testuser):
            inst_dir = os.path.join(CollectionRecordTestDirSetupMixin.dir_root, i.cdlpath)
            if not os.path.exists(inst_dir):
                os.makedirs(inst_dir)
        super(NewCollectionRecordViewTestCase, self).setUp()

    def parseARK(self, url_string):
        '''Parse the ark from the string'''
        ark_from_url = url_string[url_string.index('ark'):]
        ark_from_url = ark_from_url.rstrip('/')
        return ark_from_url

    def parsePK(self, url_string):
        pk_from_url = url_string.rstrip('/').rsplit('/',1)[1]
        return pk_from_url

    def fill_form_values(self, form):
        '''Helper function to fill in form values for valid submission
        form is an Webtest response.form object
        '''
        #fill out basic info only,required fields only
        form['title'] = 'Test Title'
        form['title_filing'] = 'Test Filing Title'
        form['date_dacs'] = 'circa 1980'
        form['date_iso'] = '1980'
        form['local_identifier'] = 'LOCALID-test'
        form['extent'] = 'loads of boxes'
        form['abstract'] = 'a nice test collection'
        form['accessrestrict'] = 'public domain'
        #form['userestrict'] = 'go craxy'
        #form['acqinfo'] = 'by mark'
        form['scopecontent'] = 'test content'

    def createNewMinimalCR(self):
        '''A helper function to create a new Collection Record with
        a known set of data
        '''
        url = reverse('collection_record_add')
        response = self.app.get(url, user='testuser')
        form = response.form
        #fill out basic info only,required fields only
        self.fill_form_values(form)
        response = form.submit(user='testuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)
        #can't test without a live server, xtf needs to talk to
        pk_from_url = self.parsePK(response.request.url)
        cr=CollectionRecord.objects.get(pk=pk_from_url)
        response = self.app.get(cr.get_edit_url(), user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'Test Title')

    def testNewView(self):
        '''Test the view for creating new collection records.
        View needs to be login protected.
        '''
        url = reverse('collection_record_add')
        response = self.app.get(url)
        self.failUnlessEqual('302 FOUND', response.status)
        self.failUnlessEqual(302, response.status_code)
        self.assertTrue(settings.LOGIN_URL+'?next='+quote(url), response.headers['location'])
        response = self.app.get(url, user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'itle')
        self.assertContains(response, '<option value="eng" selected="selected">English</option>')
        self.assertContains(response, 'access')
        self.assertContains(response, 'person')
        self.assertContains(response, 'family')
        form = response.form
        response = form.submit(user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertTemplateUsed(response,'collection_record/collection_record/add.html') 
        self.createNewMinimalCR()

    def testDuplicateLocalID(self):
        '''Test that duplicate local IDs can be entered. Some insts use a 
        boilerplate identical string for all their collections.
        '''
        url = reverse('collection_record_add')
        response = self.app.get(url, user='testuser')
        self.failUnlessEqual(200, response.status_code)
        form = response.form
        #fill out basic info only,required fields only
        form['title'] = 'Test Title'
        form['title_filing'] = 'Test Filing Title'
        form['date_dacs'] = 'circa 1980'
        form['date_iso'] = '1980'
        form['local_identifier'] = 'LOCALID-test'
        form['extent'] = 'loads of boxes'
        form['abstract'] = 'a nice test collection'
        form['accessrestrict'] = 'public domain'
        form['userestrict'] = 'go craxy'
        form['acqinfo'] = 'by mark'
        form['scopecontent'] = 'test content'
        response = form.submit(user='testuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'LOCALID')
        url = reverse('collection_record_add')
        response = self.app.get(url, user='testuser')
        self.failUnlessEqual(200, response.status_code)
        form = response.form
        #fill out basic info only,required fields only
        form['title'] = 'Test Title'
        form['title_filing'] = 'NO DUP Test Filing Title'
        form['date_dacs'] = 'circa 1980'
        form['date_iso'] = '1980'
        form['local_identifier'] = 'LOCALID-test'
        form['extent'] = 'loads of boxes'
        form['abstract'] = 'a nice test collection'
        form['accessrestrict'] = 'public domain'
        form['userestrict'] = 'go craxy'
        form['acqinfo'] = 'by mark'
        form['scopecontent'] = 'test content'
        response = form.submit(user='testuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)

    def testNewWithDCView(self):
        url = reverse('collection_record_add')
        response = self.app.get(url, user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertTemplateUsed(response,'collection_record/collection_record/add.html') 
        form = response.form
        #fill out basic info only,required fields only
        form['title'] = 'Test 2 Title'
        form['title_filing'] = 'Test Filing Title'
        form['date_dacs'] = 'circa 1980'
        form['date_iso'] = '1980'
        form['local_identifier'] = 'LOCALID-test'
        form['extent'] = 'loads of boxes'
        form['abstract'] = 'a nice test collection'
        form['accessrestrict'] = 'public domain'
        form['userestrict'] = 'go craxy'
        form['acqinfo'] = 'by mark'
        form['scopecontent'] = 'test content'
        form['person-0-content'] = 'mark redar'
        form['family-0-content'] = 'redar'
        response = form.submit(user='testuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)
        #goto edit page to confirm, need live server to test view
        pk_from_url = self.parsePK(response.request.url)
        #ark_from_url = self.parseARK(response.request.url)
        cr=CollectionRecord.objects.get(pk=pk_from_url)
        response = self.app.get(cr.get_edit_url(), user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'Test 2 Title')
        self.assertContains(response, 'redar')
        self.assertTemplateUsed(response,'collection_record/collection_record/edit.html') 

    def testNewWithARK(self):
        '''Test the collection editor basic function when you've got an ARK already
        '''
        url = reverse('collection_record_add')
        response = self.app.get(url, user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'itle')
        self.assertContains(response, '<option value="eng" selected="selected">English</option>')
        self.assertContains(response, 'access')
        self.assertContains(response, 'person')
        self.assertContains(response, 'family')
        form = response.form
        response = form.submit(user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertTemplateUsed(response,'collection_record/collection_record/add.html') 
        form = response.form
        #fill out basic info only,required fields only
        form['ark'] = 'hh' #bad ark should fail
        form['title'] = 'Test Title'
        form['title_filing'] = 'Test Filing Title'
        form['date_dacs'] = 'circa 1980'
        form['date_iso'] = '1980'
        form['local_identifier'] = 'LOCALID-test'
        form['extent'] = 'loads of boxes'
        form['abstract'] = 'a nice test collection'
        form['accessrestrict'] = 'public domain'
        form['userestrict'] = 'go craxy'
        form['acqinfo'] = 'by mark'
        form['scopecontent'] = 'test content'
        response = form.submit(user='testuser')
        self.assertTemplateUsed(response,'collection_record/collection_record/add.html') 
        form=response.form
        testark = 'ark:/99999/fk45b0b4n'
        form['ark'] = testark
        response = form.submit(user='testuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'LOCALID')
        cr=CollectionRecord.objects.get(ark=testark)
        response = self.app.get(cr.get_edit_url(), user='testuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'Test Title')
        self.assertTemplateUsed(response,'collection_record/collection_record/edit.html') 

    def testLongInput(self):
        '''Test that form invalid on long inputs (title, extent, all char fields)
        '''
        def check_resp_error_field(self, form, fieldname):
            response = form.submit(user='oactestuser')
            self.failUnlessEqual(200, response.status_code)
            self.assertContains(response, 'errors below')
            self.assertContains(response, CollectionRecord._meta.get_field_by_name(fieldname)[0].max_length)
            return response.form
        def check_resp_success(self, form):
            response = form.submit(user='oactestuser')
            self.failUnlessEqual(302, response.status_code)
            response = response.follow()
            self.failUnlessEqual(200, response.status_code)
        def get_form_and_fill(self, url):
            response = self.app.get(url, user='oactestuser')
            form = response.form
            self.fill_form_values(form)
            return form

        url_add = reverse('collection_record_add')

        form = get_form_and_fill(self, url_add)
        form['title'] = 'x' * 513
        form = check_resp_error_field(self, form, 'title')
        self.fill_form_values(form)
        form['title'] = 'x' * 512
        check_resp_success(self, form)
        form = get_form_and_fill(self, url_add)
        form['title_filing'] = 'x' * 256
        form = check_resp_error_field(self, form, 'title_filing')
        form['title_filing'] = 'x' * 255
        check_resp_success(self, form)
        form = get_form_and_fill(self, url_add)
        form['title_filing'] = '0'
        form['extent'] = 'x' * 1001
        form = check_resp_error_field(self, form, 'extent')
        form['extent'] = 'x' * 1000
        check_resp_success(self, form)
        form = get_form_and_fill(self, url_add)
        form['title_filing'] = '1'
        form['date_dacs'] = 'x' * 129
        form = check_resp_error_field(self, form, 'date_dacs')
        form['date_dacs'] = 'x' * 128
        check_resp_success(self, form)
        form = get_form_and_fill(self, url_add)
        form['title_filing'] = '2'
        form['date_iso'] = 'x' * 129
        form = check_resp_error_field(self, form, 'date_iso')
        form['date_iso'] = 'x' * 128
        check_resp_success(self, form)
        form = get_form_and_fill(self, url_add)
        form['title_filing'] = '3'
        form['local_identifier'] = 'x' * 256
        form = check_resp_error_field(self, form, 'local_identifier')
        form['local_identifier'] = 'x' * 255
        check_resp_success(self, form)


from collection_record.is_oac import is_OAC
if is_OAC():
    class CollectionRecordOACViewTestCase(CollectionRecordTestDirSetupMixin, LiveServerTestCase):
        '''Test the annotated view from the xtf. We add a couple of elements (edit button)
        There needs to be a working DSC OAC xtf running on the host specified in 
        the env var FINDAID_HOSTNAME
        '''
        fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'collection_record.publishinginstitution.json', 'collection_record.auth.user.json']
    
        def setUp(self):
            # Start a test server and tell selenium where to find it.
            live_server = self.live_server_url.replace('http://', '')
            os.environ['BACK_SERVER'] = live_server
            #self.start_test_server('localhost', 8080)
            super(CollectionRecordOACViewTestCase, self).setUp()
    
        def tearDown(self):
            #self.stop_test_server()
            super(CollectionRecordOACViewTestCase, self).tearDown()
    
        def testOACView(self):
            rec = CollectionRecord.objects.get(pk="1")
            url = rec.get_absolute_url()
            url = self.live_server_url+url
            response = self.client.get(url)
            self.failUnlessEqual(302, response.status_code)
            ret = self.client.login(username='testuser',password='testuser')
            self.failUnless(ret)
            response = self.client.get(url)
            self.failUnlessEqual(200, response.status_code)
            #Need a live serverfor this to work....
            self.assertContains(response, 'First Test Title')
            self.assertContains(response, 'localid')
            self.assertContains(response, 'Bancroft')
            self.assertContains(response, rec.get_edit_url())
            self.assertContains(response, 'logout')
    
        def testOACViewNotOwner(self):
            '''Check that the "Edit" button link doesn't appear in the preview
            for people who can't edit the findaid
            '''
            rec = CollectionRecord.objects.get(pk="1")
            url = rec.get_absolute_url()
            url = self.live_server_url+url
            response = self.client.get(url)
            self.failUnlessEqual(302, response.status_code)
            ret = self.client.login(username='testuser',password='testuser')
            self.failUnless(ret)
            response = self.client.get(url)
            self.failUnlessEqual(200, response.status_code)
            #Need a live serverfor this to work....
            self.assertContains(response, 'First Test Title')
            self.assertContains(response, 'localid')
            self.assertContains(response, 'Bancroft')
            self.assertNotContains(response, rec.get_edit_url())
            self.assertContains(response, 'logout')


class CollectionRecordPermissionsBackendTestCase(CollectionRecordTestDirSetupMixin, TestCase):
    '''test the permission backend for the Collection record app
    '''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'collection_record.publishinginstitution.json', 'collection_record.auth.user.json']

    def setUp(self):
        self.backend = CollectionRecordPermissionBackend()
        super(CollectionRecordPermissionsBackendTestCase, self).setUp()

    def testUserNotAuthenticated(self):
        '''Test when the user object has not been authenticated
        '''
        u = User.objects.get(pk=1)
        self.backend.has_perm(u, 'collection_record.change_collectionrecord')

    def testNoObject(self):
        u = User.objects.get(pk=1)
        self.backend.has_perm(u, 'collection_record.change_collectionrecord')


class SupplementalFileTestCase(CollectionRecordTestDirSetupMixin, TestCase):
    '''Test the supplemental files'''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'collection_record.supplementalfile.json', 'collection_record.publishinginstitution.json', 'collection_record.auth.user.json']

    def setUp(self):
        super(SupplementalFileTestCase, self).setUp()
        cr = CollectionRecord.objects.get(ark='ark:/99999/fk46h4rq4') 
        debug_print( "SUPP DIR" + cr.dir_supplemental_files)
        if not os.path.isdir(cr.dir_supplemental_files):
            os.makedirs(cr.dir_supplemental_files)
        fixtures_dir = os.path.abspath(os.path.join(os.path.split(__file__)[0], '../', 'fixtures'))
        pdf_test_files = glob.glob(os.path.join(fixtures_dir, '*.pdf'))
        debug_print("PDF TEST FILES:::" + str(pdf_test_files))
        for f in pdf_test_files:
            shutil.copy(f, cr.dir_supplemental_files)

    def testURL(self):
        '''Check that the url is correct for a file'''
        sf = SupplementalFile.objects.get(pk=53)
    
    def testTextFilePath(self):
        '''Check that the name of the txt file is correct'''
        sf = SupplementalFile.objects.get(pk=53)
        self.assertTrue(sf.txt_file_path[-3:] == 'txt')

    def testFileHandle(self):
        sf = SupplementalFile.objects.get(pk=53)
        sf.get_filehandle( mode='rb')

    def testRipToText(self):
        sf = SupplementalFile.objects.get(pk=53)
        from collection_record.is_oac import is_OAC
        OAC = is_OAC()
        if OAC:
            sf.rip_to_text()
