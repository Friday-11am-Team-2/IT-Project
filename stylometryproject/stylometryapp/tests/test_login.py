from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.http import JsonResponse

from ..models import *
from ..views import *


class LoginTestCase(TestCase):
    
    # Attributes for Tests
    client = None


    def setUp(self):
        """ Set up a test client """

        self.client = Client()


    def test_login_nav(self):
        """ Check navigation to the login page """

        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    
    def test_login(self):
        """ Test login on a created account """

        # Create User (registration tested elsewhere)
        user = User.objects.create_user(username='testuser', password='testpassword')
        user.save()

        # Login
        response = self.client.post('/login/', data = {'username': 'testuser', 'password': 'testpassword'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], '/home/')

    
    def test_registration(self):
        """ Test registration of a new account """

        # Create login info
        data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }

        # Register and check redirect chain
        response = self.client.post('/register/', data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], '/home/')
        self.assertEqual(response.redirect_chain[0][1], 302)

        # Check that the user was created
        user = User.objects.filter(username='testuser').first()
        self.assertIsNotNone(user)

    
    def test_logout(self):
        """ Test logout of an account"""

        # Create user
        user = User.objects.create_user(username='testuser', password='testpassword')
        user.save()

        # Login
        self.client.login(username='testuser', password='testpassword')

        # Logout
        response = self.client.post('/logout/', follow=True)
        self.assertEqual(response.status_code, 200)

        # Check that returns to login page
        self.assertEqual(response.redirect_chain[0][0], '/login/')
        self.assertEqual(response.redirect_chain[0][1], 302)


