from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.http import JsonResponse

from ..models import *
from ..views import *

import base64
import os

class VerificationViewTests(TestCase):
    
	user = None
	client = None
	profile = None
	text_source = None
	unknown_name = None
	unknown_content = None

	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='testuser', password='testpassword')
		self.user.save()
		self.client.login(username='testuser', password='testpassword')

		# Make a really quick test profile
		self.profile = Profile.objects.create(name="Test Profile Name", user=self.user)
		self.profile.save()

		self.text_source = "../PAN14_Model_Code/data/test_data/EE016"

		for file in os.listdir(self.text_source):
			if file.startswith("known"):
				with open(os.path.join(self.text_source, file), "tr") as f:
					Document.objects.create(profile=self.profile, title=file, text=f.read()).save()
			elif not self.unknown_content and file.startswith("unknown"):
				with open(os.path.join(self.text_source, file), "tr") as f:
					self.unknown_name = file
					self.unknown_content = f.read()
	
	def test_navigation(self):
		"""Navigation to the verification page"""
		response = self.client.get('/verify/')
		self.assertEqual(response.status_code, 200)

	def test_run_verification(self):
		"""Document Verification API Test"""

		# Define unknown data
		data_pack = {
			'profile_id': self.profile.id,
			'file_names': self.unknown_name,
			'file_contents': [self.unknown_content],
		}

		response = self.client.post('/run_verification/', data=data_pack, content_type="application/json", follow=True)
		self.assertEqual(response.status_code, 201)

	def test_text_analytics(self):
		"""Text Analytics API Test"""

		# Define test data
		data_pack = {
			'file_names': self.unknown_name,
			'file_contents': self.unknown_content,
		}

		response = self.client.post('/text_analytics/', QUERY_STRING=f"f={self.unknown_name}", data=data_pack, content_type="application/json", follow=True)
		self.assertEqual(response.status_code, 201)

		response = self.client.post('/text_analytics/', QUERY_STRING=f"p={self.profile.id}", data=data_pack, content_type="applications/json", follow=True)
		self.assertEqual(response.status_code, 201)
		

	def tearDown(self):
		self.user.delete()
		self.profile.delete()