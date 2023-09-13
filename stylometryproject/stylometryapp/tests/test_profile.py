from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.http import JsonResponse

from ..models import *
from ..views import *


class ProfileViewsTestCase(TestCase):
    """Test Case for User Story of Create Profile, Edit Profile and Delete Profile"""

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
        """ Profile Creation Test """

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

    
    def test_profile_delete(self):
        """ Profile Deletion Test """

        # Create Profile (tested elsewhere, so just manually create in DB)
        profile = Profile.objects.create(user=self.user, name='Test Profile Name')
        profile_id = profile.id

        # Delete Profile
        response = self.client.post('/delete_profile/', {'profile_id': profile.id}, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)
        self.assertEqual(response.status_code, 200)

        # Check if Deleted
        profile = Profile.objects.filter(id=profile_id).first()
        self.assertIsNone(profile)

    
    def test_profile_edit(self):
        """ Profile Edit Test """

        # Create Profile (tested elsewhere, so just manually create in DB)
        profile = Profile.objects.create(user=self.user, name='Test Profile Name')
        original_profile_name = profile.name

        # Edit Profile
        new_profile_name = 'New Profile Name'
        response = self.client.post('/edit_profile/' + str(profile.id) + '/', {'profile_name': new_profile_name}, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)

        # Check if Edited
        profile = Profile.objects.filter(id=profile.id).first()
        self.assertEqual(profile.name, new_profile_name)
        self.assertNotEqual(profile.name, original_profile_name)


    def tearDown(self):
        """ Delete the user """

        self.user.delete()



class ProfileRetrievalTestCase(TestCase):
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


    def test_get_profile_name(self):
        """ Test Retrieving Profile Name """

        # Create Profile (tested elsewhere, so just manually create in DB)
        profile = Profile.objects.create(user=self.user, name='Test Profile Name')

        # Get Profile Name
        response = self.client.get('/get_profile_name/' + str(profile.id) + '/')
        self.assertEqual(response.status_code, 200)

        # Check the Data
        data = response.json()
        self.assertEqual(data['name'], 'Test Profile Name')


    def tearDown(self):
        """ Delete the user """

        self.user.delete()