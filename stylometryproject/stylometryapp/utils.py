from django.conf import settings
import os
import threading
from stylometry import StyloNet
from django.http import HttpRequest
from .models import Profile
# file type handling
import base64
import io
from docx import Document # pip install python-docx
import PyPDF2 # pip install PyPDF2

### Stylometry Model Utils ###
stylometry_model = None

def get_stylonet() -> StyloNet:
	"""Initialize or return the existing instance of the StyloNet object"""
	global stylometry_model

	# Initialize if not already, otherwise just return existing
	if stylometry_model is None:
		try:
			profile_base = settings.STYLOMETRY_PROFILE_DIR
		except AttributeError:
			profile_base = "stylometry_models"
		
		try:
			profile = settings.STYLOMETRY_PROFILE
		except AttributeError:
			profile = os.listdir(profile_base)[0]

		stylometry_model = StyloNet(profile, profile_base)
		print(f"Initialized Stylometry Model at {id(stylometry_model)}")

	return stylometry_model

def stylonet_preload() -> None:
	"""Spawn a separate thread to preload the model"""
	preload = threading.Thread(target=get_stylonet)
	preload.start()

# File type prosessing
def convert_file(file_name, file_content):             
	#print("convert_file")
	file_extension = os.path.splitext(file_name)[1].lower()
	file_content = base64.b64decode(file_content)
	converted_content = ""

	if file_extension == '.txt':
		# leave .txt files as is
		print("txt to txt")
		converted_content = file_content.decode("utf-8")
	elif file_extension == '.docx':
		# .docx to text
		print("docx to txt")
		converted_content = convert_docx_to_txt(file_content)
	elif file_extension == '.pdf':
		# .pdf to text
		print("pdf to txt")
		converted_content = convert_pdf_to_txt(file_content)
	else:
		# unsupported file type
		print("Unsupported file type: " + file_name)
		# TO DO: popup on JS side if unsupported file type passed in?
	#print("converted content: " + converted_content)
	return converted_content

def convert_docx_to_txt(content):
	try:
		# create word document from encoded string
		doc = Document(io.BytesIO(content))
		# extract and return text
		text = ""
		for para in doc.paragraphs:
			text += para.text
		return text
	except Exception as e:
		print("Error during DOCX conversion:", str(e))
		return ""

def convert_pdf_to_txt(content):
	try:
		# create pdf from encoded string
		pdf_file = io.BytesIO(content)
		reader = PyPDF2.PdfReader(pdf_file)
		text = ""
		for page_num in range(len(reader.pages)):
			text += reader.pages[page_num].extract_text()
		return text
	except Exception as e:
		print("Error during PDF conversion:", str(e))
		return ""


# Current profile selection safety and sanity checker
def safe_profile_select(request: HttpRequest, profile_id:int = None) -> Profile|None:
	"""Allows querying and selection of current profile based on a request
	Returns the currently selected Profile or None, but only if it
	exists, is a valid profile and belongs to the user asking for it"""

	# Early exit when not selection exists
	if 'selected_profile' not in request.session and not profile_id:
		return None

	# When profile object is passed instead
	if isinstance(profile_id, Profile): profile_id = profile_id.id

	try:
		if not profile_id: profile_id = request.session['selected_profile']

		profile = Profile.objects.get(user=request.user, id=profile_id)
		request.session['selected_profile'] = profile_id

		# Return the valid selected profile
		return profile
	except (Profile.DoesNotExist, AttributeError):
		# Cleanup and return empty-handed
		request.session.pop('selected_profile')
		return None