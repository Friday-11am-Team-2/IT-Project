from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.http import JsonResponse

from ..models import *
from ..views import *

class VerificationViewTests(TestCase):
    
	user = None
	client = None

	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user.save()
        self.client.login(username='testuser', password='testpassword')
	
	def test_navigation(self):
		"""Navigation to the verification page"""
		response = self.client.get('/verify/')
		self.assertEqual(response.status_code, 200)

	def test_run_verification(self):
		"""Document Verification API Test"""
		pass
	
	def test_text_analytics(self):
		"""Text Analytics API Test"""
		pass

	def tearDown(self):
		self.user.delete()