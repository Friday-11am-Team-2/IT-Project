from django.conf import settings
import os
import threading
from stylometry import StyloNet


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
	preload = threading.Thread(target=get_stylonet())
	preload.start()

# File type prosessing (only accepts txt, docx)
def convert_file(file_name, file_content):             

	file_extension = os.path.splitext(file_name)[1].lower()
	converted_content = ""

	if file_extension == '.txt':
		# leave .txt files as is
		converted_content = file_content
		print("txt to txt")
	elif file_extension == '.docx':
		# convert .docx to .txt
		converted_content = convert_docx_to_txt(file_content)
		print("docx to txt")
	else:
		# unsupported file type
		print(f"Unsupported file type: {file_name}")
		# TO DO: deal with unsupported file type if they somehow got passed in
	#print(converted_content)
	return converted_content


def convert_docx_to_txt(file_content):
	return ""
	# import docx2txt
	# import zipfile
	# from io import BytesIO
	# from lxml import etree
	# try:
	# 	# Create a BytesIO object to work with the binary content
	# 	content_stream = BytesIO(file_content)

    #     # Open the .docx file using zipfile
	# 	with zipfile.ZipFile(content_stream) as docx:
    #         # Find and extract the document.xml file (contains text)
	# 		doc_xml_content = docx.read('word/document.xml')

    #         # Text extraction            
	# 		root = etree.fromstring(doc_xml_content)
	# 		text_content = ''.join(root.itertext())

    #         # Return the extracted text
	# 		return text_content
		
	# except Exception as e:
    #     # Handle exceptions
	# 	print(f"Error: {str(e)}")
	# 	return ""