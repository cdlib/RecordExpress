from urllib import quote
from django.test import TestCase
from django.core.urlresolvers import reverse


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class NewCollectionRecordViewTestCase(TestCase):
    fixtures = ['sites.json']#'auth.json', 'xtf.arkobjecttestcase.json']

    def testNewView(self):
        '''Test the view for creating new collection records.
        View needs to be login protected.
        '''
        url = reverse('collection_record_add')
        response = self.client.get(url)
        self.failUnlessEqual(302, response.status_code)
        self.assertRedirects(response, '/accounts/login/?next='+quote(url))
