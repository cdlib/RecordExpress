from urllib import quote
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db.models.base import ValidationError
from django_webtest import WebTest
from collection_record.forms import CollectionRecordForm
from collection_record.models import CollectionRecord

class CollectionRecordFormTestCase(TestCase):
    '''Test the form for creating new collection records. Is this form different
    from the existing record form?
    '''
    def testNewForm(self):
        f = CollectionRecordForm()
     
class NewCollectionRecordViewTestCase(WebTest):
    fixtures = ['sites.json', 'auth.json', ]

    def testNewView(self):
        '''Test the view for creating new collection records.
        View needs to be login protected.
        '''
        url = reverse('collection_record_add')
        response = self.app.get(url)
        self.failUnlessEqual('302 FOUND', response.status)
        self.failUnlessEqual(302, response.status_code)
        self.assertRedirects(response, '/accounts/login/?next='+quote(url))
        response = self.app.get(url, user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'itle')
        self.assertContains(response, '<option value="eng" selected="selected">English</option>')
        self.assertContains(response, 'access')
        self.assertContains(response, 'CR')
        self.assertContains(response, 'person')
        self.assertContains(response, 'family')
        form = response.form
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertTemplateUsed(response,'collection_record/collection_record/add.html') 
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
        self.assertTemplateUsed(response,'collection_record/collection_record/add_preview.html') 
        # get a the collection_record created and view?
        # redirect to the view page, which is indexed by ark???
        #
        response = response.form.submit(user='oactestuser')
        self.assertTemplateUsed(response,'collection_record/collection_record/added.html') 


class CollectionRecordModelTest(TestCase):
    '''Test the CollectionRecord django model'''
    def testModelExists(self):
        rec = CollectionRecord()
        self.failUnlessRaises(ValidationError, rec.full_clean)
