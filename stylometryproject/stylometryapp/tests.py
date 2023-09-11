from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse

from .models import *
from .views import *

class ProfileViewsTestCase(TestCase):
    """Test Case for User Story of Create Profile and Add Document"""

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

    def test_navigation(self):
        """ Navigate to the profile page """
        # Get the profile page
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    def test_create_profile(self):
        # Create Profile
        response = self.client.post('/create_profile/', {'name': 'Test Profile Name'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)

        # Check the Data
        data = response.json()
        self.assertEqual(data['name'], 'Test Profile Name')

        # Test the profile object
        profile = Profile.objects.filter(name='Test Profile Name').first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, 'Test Profile Name')

    def test_add_document(self):
        # Create Profile (already tested, so just manually create in DB)
        profile = Profile.objects.create(user=self.user, name='Test Profile Name')

        # Create Data to Send
        file_names = ["test_doc.txt"]
        file_contents = ["Sample Text Content"]
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
            self.assertEqual(document.text, file_contents[i])

    def tearDown(self):
        """ Delete the user """
        self.user.delete()


class ProfileModelTestCase(TestCase):
    """Test Case for Profile Operations"""

    def test_profile_creation(self):
        """ Create a user, test if it exist """
        user = User.objects.create(username='testuser')
        profile = Profile.objects.create(user=user, name='Test Name')
        self.assertEqual(profile.__str__(), 'Test Name')

    def test_profile_deletion_cascade(self):
        """ Test if deleting a profile cascades to documents """
        user = User.objects.create(username='testuser')
        profile = Profile.objects.create(user=user, name='Test Name')
        Document.objects.create(profile=profile, title='Test Doc', text='Sample Text')
        self.assertEqual(Document.objects.count(), 1)
        profile.delete()
        self.assertEqual(Document.objects.count(), 0)


class DocumentModelTestCase(TestCase):
    """Test Case for Document Operations"""

    def test_document_creation(self):
        """Test creating a document with a name"""
        user = User.objects.create(username='testuser')
        profile = Profile.objects.create(user=user, name='Test Name')
        document = Document.objects.create(profile=profile, title='Test Doc', text='Sample Text')
        self.assertEqual(document.__str__(), 'Test Doc')

    def test_document_text(self):
        """ Test creating a document with text """
        user = User.objects.create(username='testuser')
        profile = Profile.objects.create(user=user, name='Test Name')
        document = Document.objects.create(profile=profile, title='Test Doc', text='Sample Text')
        self.assertEqual(document.text, 'Sample Text')

    def test_document_deletion(self):
        """ Test deleting a document """
        user = User.objects.create(username='testuser')
        profile = Profile.objects.create(user=user, name='Test Name')
        document = Document.objects.create(profile=profile, title='Test Doc', text='Sample Text')
        document_id = document.id
        document.delete()
        with self.assertRaises(Document.DoesNotExist):
            Document.objects.get(id=document_id)