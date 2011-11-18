from urllib import quote
from django.test import TestCase
from django.core.urlresolvers import reverse
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
        self.assertContains(response, '<option value="eng" selected="selected">English</option>')
        self.assertContains(response, 'access')
        self.assertContains(response, 'CR')
        self.assertContains(response, 'person')
        self.assertContains(response, 'family')
        postdata = {
                'ark':'',
                'title':'Test Title',
                'title_filing':'TEST Filing Title',
                'local_identifier':'Local test ID',
                'language':'eng',
                'accessrestrict':'test access cond',
                'userestrict':'test pub rights',
                'acqinfo':'test acq info',
                'bioghist':'test biog',
                'scopecontent':'test scope',
                'online_items_url':'http://www.oac.cdlib.org',
                'person-TOTAL_FORMS':1,
                'person-INITIAL_FORMS':0,
                'person-MAX_NUM_FORMS':'',
                'person-0-content':'test personname',
                'person-0-qualifier':'person',
                'person-0-term':'CR',
                'family-TOTAL_FORMS':1,
                'family-INITIAL_FORMS':0,
                'family-MAX_NUM_FORMS':'',
                'family-0-content':'test familyname',
                'family-0-qualifier':'family',
                'family-0-term':'CR',
                }
        response = self.client.post(url, data=postdata)
        self.failUnlessEqual(200, response.status_code)
        print response
