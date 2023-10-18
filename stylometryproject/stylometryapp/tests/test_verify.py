from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.http import JsonResponse

from ..models import *
from ..views import *
import base64

class VerificationViewTests(TestCase):
    
	user = None
	client = None
	profile = None

	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='testuser', password='testpassword')
		self.user.save()
		self.client.login(username='testuser', password='testpassword')

		# Make a really quick test profile
		self.profile = Profile(name = "Test Profile Name", user=self.user)
		self.profile.save()

		known_name = "test.txt"
		known_content = "Lorem ipsum dolor sit"
		Document.objects.create(profile=self.profile, title=known_name, text=known_content)
	
	def test_navigation(self):
		"""Navigation to the verification page"""
		response = self.client.get('/verify/')
		self.assertEqual(response.status_code, 200)

	def test_run_verification(self):
		pass

	def test_text_analytics(self):
		"""Text Analytics API Test"""

		# Define test data
		names = ["unknown.txt"]
		content = ["consectetur adipiscing elit, sed do eiusmod tempor \
		     incididunt ut labore et dolore magna aliqua"]
		data_pack = {
			'file_names': names,
			'file_contents': content,
		}

		response = self.client.post('/text_analytics/', QUERY_STRING=f"f={names[0]g}", data=data_pack, content_type="application/json", follow=True)
		self.assertEqual(response.status_code, 201)

		response = self.client.post('/text_analytics/', QUERY_STRING=f"p={self.profile.id}", data=data_pack, content_type="applications/json", follow=True)
		self.assertEqual(response.status_code, 201)
		

	def tearDown(self):
		self.user.delete()
		self.profile.delete()