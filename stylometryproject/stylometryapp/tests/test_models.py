from django.test import TestCase
from django.contrib.auth.models import User

from ..models import *


class ProfileModelTestCase(TestCase):
    """Test Case for Profile Operations"""

    def test_profile_creation(self):
        """ Create a user, test if it exist """

        # Create User
        user = User.objects.create(username='testuser')

        # Create Profile
        profile = Profile.objects.create(user=user, name='Test Name')
        self.assertEqual(profile.__str__(), 'Test Name')


    def test_profile_deletion_cascade(self):
        """ Test if deleting a profile cascades to documents """
        
        # Create User
        user = User.objects.create(username='testuser')

        # Create Profile
        profile = Profile.objects.create(user=user, name='Test Name')

        # Create Document
        Document.objects.create(profile=profile, title='Test Doc', text='Sample Text')

        # Compare Counts before and after Deletion
        self.assertEqual(Document.objects.count(), 1)
        profile.delete()
        self.assertEqual(Document.objects.count(), 0)



class DocumentModelTestCase(TestCase):
    """Test Case for Document Operations"""

    def test_document_creation(self):
        """Test creating a document with a name"""

        # Create User
        user = User.objects.create(username='testuser')

        # Create Profile
        profile = Profile.objects.create(user=user, name='Test Name')

        # Create Document and Test
        document = Document.objects.create(profile=profile, title='Test Doc', text='Sample Text')
        self.assertEqual(document.__str__(), 'Test Doc')


    def test_document_text(self):
        """ Test creating a document with text """

        # Create User
        user = User.objects.create(username='testuser')

        # Create Profile
        profile = Profile.objects.create(user=user, name='Test Name')

        # Create Document with Text and Test
        document = Document.objects.create(profile=profile, title='Test Doc', text='Sample Text')
        self.assertEqual(document.text, 'Sample Text')


    def test_document_deletion(self):
        """ Test deleting a document """

        # Create User
        user = User.objects.create(username='testuser')

        # Create Profile
        profile = Profile.objects.create(user=user, name='Test Name')

        # Create Document and get ID
        document = Document.objects.create(profile=profile, title='Test Doc', text='Sample Text')
        document_id = document.id

        # Delete Document and check if it is gone from DB
        document.delete()
        with self.assertRaises(Document.DoesNotExist):
            Document.objects.get(id=document_id)

