from urllib import quote
from django.test import TestCase
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from collection_record.forms import CollectionRecordForm

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


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
        #self.failUnlessEqual('200 OK', response.status)
        #form = response.forms['institution_form']
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
        #self.assertTemplateUsed(response,'collection_record/collection_record/add_preview.html') 
        # get a the collection_record created and view?
