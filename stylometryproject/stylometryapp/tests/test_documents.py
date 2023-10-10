from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse

from ..models import *
from ..views import *
import base64

class DocumentManageTestCase(TestCase):
    """Test Case for Adding and Deleting a Document"""

    # Attributes for Tests
    user = None
    client = None


    def setUp(self):
        """ Set up a test client """

        # Create user to test and login
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user.save()
        self.client.login(username='testuser', password='testpassword')


    def test_add_document(self):
        """ Test Adding a Document """  

        # Create Profile (tested elsewhere, so just manually create in DB)
        profile = Profile.objects.create(user=self.user, name='Test Profile Name')

        # Create Data to Send
        file_names = ["test_doc.txt"]
        text_content = "Sample Text Content"
        file_contents = [base64.b64encode(text_content.encode()).decode('utf-8')]
        data_to_send = {
            'profile_id': profile.id, 
            'file_names': file_names, 
            'file_contents': file_contents
            }
        data_to_send = json.dumps(data_to_send)

        # Add Document
        response = self.client.post('/add_profile_docs/', data=data_to_send, content_type="application/json", follow=True)
        self.assertEqual(response.status_code, 201)

        # Test the documents
        for i in range(len(file_names)):
            document = Document.objects.filter(title=file_names[i]).first()
            self.assertIsNotNone(document)
            self.assertEqual(document.title, file_names[i])
            self.assertEqual(document.text, text_content)


    def test_delete_document(self):
        """ Test Deleting a Document """

        # Create Profile (tested elsewhere, so just manually create in DB)
        profile = Profile.objects.create(user=self.user, name='Test Profile Name')

        # Create Document (tested elsewhere, so just manually create in DB)
        document = Document.objects.create(profile=profile, title='Test Doc', text='Sample Text')

        # Delete Document
        response = self.client.post('/delete_document/' + str(document.id) + '/', follow=True)
        self.assertEqual(response.status_code, 200)

    
    def test_get_documents(self):
        """ Test getting all Document names of a Profile """

        # Create Profile (tested elsewhere, so just manually create in DB)
        profile = Profile.objects.create(user=self.user, name='Test Profile Name')

        # Create Documents (tested elsewhere, so just manually create in DB)
        num_docs = 5
        for i in range (num_docs):
            Document.objects.create(profile=profile, title='Test Doc ' + str(i), text='Sample Text ' + str(i))

        # Get Documents
        response = self.client.get('/get_documents/' + str(profile.id) + '/', follow=True)
        self.assertEqual(response.status_code, 200)

        # Check the Data
        data = response.json()
        self.assertEqual(len(data), num_docs)
        for i in range (num_docs):
            self.assertEqual(data[i]['title'], 'Test Doc ' + str(i))


    def tearDown(self):
        """ Delete the user """
        self.user.delete()