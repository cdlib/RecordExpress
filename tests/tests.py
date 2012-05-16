import os
from urllib import quote
import xml.etree.ElementTree as ET
from shutil import rmtree
from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db.models.base import ValidationError
from django.contrib.auth.models import User
from django_webtest import WebTest
from liveTestCase import TestCaseLiveServer
from collection_record.forms import CollectionRecordForm
from collection_record.models import CollectionRecord
from collection_record.models import SupplementalFile
from collection_record.perm_backend import CollectionRecordPermissionBackend

class CollectionRecordModelTest(TestCase):
    '''Test the CollectionRecord django model'''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'collection_record.supplementalfile.json', 'oac.institution.json', 'oac.groupprofile.json']#['sites.json', 'auth.json', 

    def tearDown(self):
        dir_root = os.path.join(os.path.abspath(os.path.split(__file__)[0]), 'data')
        if os.path.isdir(dir_root):
            rmtree(dir_root)

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
        rec = CollectionRecord.objects.get(pk="ark:/13030/c8s180ts")
        ead_xml = rec.ead_xml
        self.failUnless(ead_xml.index('<ead>') >= 62)
        self.failUnless('ark:/13030/c8s180ts' in ead_xml)
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

    def testEAD_iso_date(self):
        '''Check that the unitdate "normal" attribute only shows up for 
        records with date_iso
        '''
        rec = CollectionRecord.objects.get(pk="ark:/99999/fk4vh5x06")
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
        rec = CollectionRecord.objects.get(pk="ark:/13030/c8s180ts")
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
        rec = CollectionRecord.objects.get(pk="ark:/99999/fk46h4rq4")
        ead_xml = rec.ead_xml
        try:
            ET.fromstring(ead_xml)
        except:
            self.fail('ElementTree could not parse xml')
        self.failUnless('</archdesc>' in ead_xml)
        self.failUnless('<otherfindaid' in ead_xml)
        self.failUnless('</extref>' in ead_xml)
        self.failUnless('index-nosoup.html' in ead_xml)

    def testEAD_file_save(self):
        rec = CollectionRecord.objects.get(pk="ark:/13030/c8s180ts")
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
        rec = CollectionRecord.objects.get(pk="ark:/99999/fk46h4rq4")
        url = rec.get_xml_url
        self.failUnless(url is not None)

    def testEAD_file_remove_on_delete(self):
        '''Test that the EAD xml file is removed when the Collection Record is 
        deleted
        '''
        rec = CollectionRecord.objects.get(pk="ark:/13030/c8s180ts")
        dir_root = os.path.join(os.path.abspath(os.path.split(__file__)[0]), 'data')
        rec.dir_root = dir_root
        if not os.path.isdir(rec.ead_dir):
            os.makedirs(rec.ead_dir)
        rec.save_ead_file()
        ead_fname = rec.ead_filename
        rec.delete()
        if os.path.exists(ead_fname):
            self.fail('Did not delete ead file %s' % (ead_fname,))


class CollectionRecordFormTestCase(TestCase):
    '''Test the form for creating new collection records. Is this form different
    from the existing record form?
    '''
    def testNewForm(self):
        f = CollectionRecordForm()
     

class CollectionRecordViewAllTestCase(TestCase):
    '''Test the view of all collection records for a a user
    '''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'oac.institution.json', 'oac.groupprofile.json', 'sites.json', 'auth.json', ]

    def testViewAllCollectionRecords(self):
        '''Verify that the user can see their institution's collection records
        and not others.
        '''
        url = reverse('collection_record_view_all', args=None)
        ret = self.client.login(username='oactestuser',password='oactestuser')
        response = self.client.get(url)
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'Collection')
        self.assertContains(response, '0')
        self.assertContains(response, 'fk4vh5x06')
        ret = self.client.login(username='oactestsuperuser', password='oactestsuperuser')
        self.failUnless(ret)
        response = self.client.get(url)
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'Collection')
        self.assertContains(response, '5')
        self.assertContains(response, 'fk42r40zx')
        
    def testLinksOnCollectionRecordListPage(self):
        '''Check that some links do exist on the collection record list page
        '''
        url = reverse('collection_record_view_all', args=None)
        ret = self.client.login(username='oactestuser',password='oactestuser')
        response = self.client.get(url)
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'fk4vh5x06')
        url_add = reverse('collection_record_add', args=None)
        self.assertContains(response, url_add)
        rec = CollectionRecord.objects.get(pk='ark:/99999/fk4vh5x06')
        url_rec = rec.get_absolute_url()
        self.assertContains(response, url_rec)
        url_xml = rec.get_xml_url()
        self.assertContains(response, url_xml)

#TODO:this is going to require a live test server for xtf to talk to
###class CollectionRecordXMLViewTestCase(WebTest):
###    '''Test views of the CollectionRecord'''
###    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'oac.institution.json', 'oac.groupprofile.json', 'sites.json', 'auth.json', ]
###
###    def testXMLView(self):
###        rec = CollectionRecord.objects.get(pk="ark:/13030/c8s180ts")
###        url = rec.get_absolute_url() + '/xml/'
###        ret = self.client.login(username='oactestuser',password='oactestuser')
###        response = self.client.get(url)
###        self.failUnlessEqual(200, response.status_code)
###        self.assertContains(response, '<ead>')
###        self.assertContains(response, 'Banc')


class CollectionRecordEditTestCase(WebTest):
    '''Test the edit page for the collection records. Should be able to modify
    all data (main & assoc. DCs) and delete and add DC stored data
    '''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'oac.institution.json', 'oac.groupprofile.json', 'sites.json', 'auth.json', ]

    def testEditPageAuth(self):
        rec = CollectionRecord.objects.get(pk="ark:/13030/c8s180ts")
        url = rec.get_edit_url()
        response = self.app.get(url)
        self.failUnlessEqual('302 FOUND', response.status)
        self.failUnlessEqual(302, response.status_code)
        self.assertTrue(settings.LOGIN_URL+'?next='+quote(url), response.headers['location'])
        response = self.app.get(url, user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'itle')
        self.assertContains(response, '<option value="eng" selected="selected">English</option>')
        self.assertContains(response, 'access')
        self.assertContains(response, 'logout')

    def testEditAttr(self):
        '''Edit a directly associated value of the Record'''
        rec = CollectionRecord.objects.get(pk="ark:/99999/fk46h4rq4")
        url = rec.get_edit_url()
        response = self.app.get(url, user='oactestuser')
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
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(302, response.status_code)
        response.follow()
        self.assertTemplateUsed(response,'collection_record/collection_record/ead_template.xml') 
        response = self.app.get(url, user='oactestuser')
        self.assertContains(response, 'logout')
        form = response.forms['main_form']
        form['title'] = ''
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertTemplateUsed(response,'collection_record/collection_record/edit.html') 
        self.assertContains(response, 'errorlist')

    def testEditDCTerm(self):
        '''Test the editing of a term stored in an associated DC object
        '''
        rec = CollectionRecord.objects.get(pk="ark:/13030/c8s180ts")
        url = rec.get_edit_url()
        response = self.app.get(url, user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'logout')
        form = response.forms['main_form']
        newPerson = 'Mark Redar Test'
        form['person-0-content'] = newPerson
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(302, response.status_code)
        #self.assertRedirects(response, rec.get_absolute_url())
        response.follow(user='oactestuser')
        self.assertTemplateUsed(response,'collection_record/collection_record/ead_template.xml') 
        #NOTE: Currently can't test the updated "view" of the object because
        # of the xtf interaction, it goes to live back server
        response = self.app.get(url, user='oactestuser')
        self.assertTrue(newPerson in response)
        self.assertContains(response, newPerson)
        self.assertContains(response, 'logout')
        response = self.app.get(url, user='oactestuser')
        form['person-0-content'] = ''
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'errorlist')

    def testDeletionOfDCTerm(self):
        '''Test the deletion of a term'''
        pass

class NewCollectionRecordViewTestCase(WebTest):
    fixtures = ['sites.json', 'auth.json', 'oac.institution.json', 'oac.groupprofile.json']
    def setUp(self):
        '''Override the "databases" config file to use the test shoulder'''
        os.environ['DATABASES_XML_FILE'] = os.path.join(os.environ['HOME'], '.databases-test.xml')

    def parseARK(self, url_string):
        '''Parse the ark from the string'''
        ark_from_url = url_string[url_string.index('ark'):]
        ark_from_url = ark_from_url.rstrip('/')
        return ark_from_url

    def createNewMinimalCR(self):
        '''A helper function to create a new Collection Record with
        a known set of data
        '''
        url = reverse('collection_record_add')
        response = self.app.get(url, user='oactestuser')
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
        #form['userestrict'] = 'go craxy'
        #form['acqinfo'] = 'by mark'
        form['scopecontent'] = 'test content'
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)
        self.assertTrue('ark:' in response.request.url)
        #can't test without a live server, xtf needs to talk to
        ark_from_url = self.parseARK(response.request.url)
        cr=CollectionRecord.objects.get(ark=ark_from_url)
        response = self.app.get(cr.get_edit_url(), user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'ark:')
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
        response = self.app.get(url, user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'itle')
        self.assertContains(response, '<option value="eng" selected="selected">English</option>')
        self.assertContains(response, 'access')
        self.assertContains(response, 'person')
        self.assertContains(response, 'family')
        form = response.form
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertTemplateUsed(response,'collection_record/collection_record/add.html') 
        self.createNewMinimalCR()

    def testDuplicateLocalID(self):
        '''Test that duplicate local IDs can be entered. Some insts use a 
        boilerplate identical string for all their collections.
        '''
        url = reverse('collection_record_add')
        response = self.app.get(url, user='oactestuser')
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
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)
        self.assertTrue('ark:' in response.request.url)
        self.assertContains(response, 'ark:')
        url = reverse('collection_record_add')
        response = self.app.get(url, user='oactestuser')
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
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)

    def testNewWithDCView(self):
        url = reverse('collection_record_add')
        response = self.app.get(url, user='oactestuser')
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
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)
        #goto edit page to confirm, need live server to test view
        ark_from_url = response.request.url[response.request.url.index('ark:'):]
        ark_from_url = ark_from_url.rstrip('/')
        cr=CollectionRecord.objects.get(ark=ark_from_url)
        response = self.app.get(cr.get_edit_url(), user='oactestuser')
        self.assertContains(response, 'ark:')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'ark:')
        self.assertContains(response, 'Test 2 Title')
        self.assertContains(response, 'redar')
        self.assertTemplateUsed(response,'collection_record/collection_record/edit.html') 

    def testNewWithARK(self):
        '''Test the collection editor basic function when you've got an ARK already
        '''
        url = reverse('collection_record_add')
        response = self.app.get(url, user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'itle')
        self.assertContains(response, '<option value="eng" selected="selected">English</option>')
        self.assertContains(response, 'access')
        self.assertContains(response, 'person')
        self.assertContains(response, 'family')
        form = response.form
        response = form.submit(user='oactestuser')
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
        response = form.submit(user='oactestuser')
        self.assertTemplateUsed(response,'collection_record/collection_record/add.html') 
        form=response.form
        testark = 'ark:/99999/fk45b0b4n'
        form['ark'] = testark
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)
        self.assertTrue('ark:' in response.request.url)
        self.assertContains(response, 'ark:')
        cr=CollectionRecord.objects.get(ark=testark)
        response = self.app.get(cr.get_edit_url(), user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'ark:')
        self.assertContains(response, 'Test Title')
        self.assertTemplateUsed(response,'collection_record/collection_record/edit.html') 


class CollectionRecordOACViewTestCase(TestCaseLiveServer):
    '''Test the annotated view from the xtf. We add a couple of elements (edit button)
    There needs to be a working DSC OAC xtf running on the host specified in 
    the env var FINDAID_HOSTNAME
    '''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'oac.institution.json', 'oac.groupprofile.json', 'sites.json', 'auth.json', ]
    def setUp(self):
        # Start a test server and tell selenium where to find it.
        os.environ['BACK_SERVER'] = 'localhost:8080'
        self.start_test_server('localhost', 8080)

    def tearDown(self):
        self.stop_test_server()

    def testOACView(self):
        rec = CollectionRecord.objects.get(pk="ark:/13030/c8s180ts")
        url = rec.get_absolute_url()
        response = self.client.get(url)
        self.failUnlessEqual(302, response.status_code)
        ret = self.client.login(username='oactestuser',password='oactestuser')
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
        rec = CollectionRecord.objects.get(pk="ark:/13030/c8s180ts")
        url = rec.get_absolute_url()
        response = self.client.get(url)
        self.failUnlessEqual(302, response.status_code)
        ret = self.client.login(username='oactest',password='oactest')
        self.failUnless(ret)
        response = self.client.get(url)
        self.failUnlessEqual(200, response.status_code)
        #Need a live serverfor this to work....
        self.assertContains(response, 'First Test Title')
        self.assertContains(response, 'localid')
        self.assertContains(response, 'Bancroft')
        self.assertNotContains(response, rec.get_edit_url())
        self.assertContains(response, 'logout')


class CollectionRecordPermissionsBackendTestCase(TestCase):
    '''test the permission backend for the Collection record app
    '''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'oac.institution.json', 'oac.groupprofile.json', 'auth.json', ]

    def setUp(self):
        self.backend = CollectionRecordPermissionBackend()

    def testUserNotAuthenticated(self):
        '''Test when the user object has not been authenticated
        '''
        u = User.objects.get(pk=1)
        self.backend.has_perm(u, 'collection_record.change_collectionrecord')

    def testNoObject(self):
        u = User.objects.get(pk=1)
        self.backend.has_perm(u, 'collection_record.change_collectionrecord')


class SupplementalFileTestCase(TestCase):
    '''Test the supplemental files'''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'collection_record.supplementalfile.json', ]#'oac.institution.json', 'oac.groupprofile.json']#['sites.json', 'auth.json', 

    def testURL(self):
        '''Check that the url is correct for a file'''
        f = SupplementalFile.objects.get(pk=53)
