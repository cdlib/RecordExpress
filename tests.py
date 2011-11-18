from urllib import quote
from django.test import TestCase
from django.core.urlresolvers import reverse
from collection_record.forms import NewCollectionRecordForm

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class NewCollectionRecordFormTestCase(TestCase):
    '''Test the form for creating new collection records. Is this form different
    from the existing record form?
    '''
    def testNewForm(self):
        f = NewCollectionRecordForm()
     
class NewCollectionRecordViewTestCase(TestCase):
    fixtures = ['sites.json', 'auth.json', ]

    def testNewView(self):
        '''Test the view for creating new collection records.
        View needs to be login protected.
        '''
        url = reverse('collection_record_add')
        response = self.client.get(url)
        self.failUnlessEqual(302, response.status_code)
        self.assertRedirects(response, '/accounts/login/?next='+quote(url))
        ret = self.client.login(username='oactestuser',password='oactestuser')
        self.failUnless(ret)
        response = self.client.get(url)
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'itle')
        print response
