from django.conf import settings
from Stylometry import StyloNet

### Stylometry Model Utils ###
stylometry_model: StyloNet|None = None

def getStyloNet() -> StyloNet:
	"""Initialize or return the existing instance of the StyloNet object"""
	global stylometry_model

	# Initialize if not already, otherwise just return existing
	if stylometry_model is None:
		stylometry_model = StyloNet(settings.STYLOMETRY_DIR, settings.STYLOMETRY_MATCH_THRESHOLD)
		print(f"Initialized Stylometry Model at {id(stylometry_model)}")

	return stylometry_model

# # File type prosessing (only accepts txt, docx)
# def convert_file(file_name, file_content):             

# 	file_extension = os.path.splitext(file_name)[1].lower()
# 	converted_content = ""

# 	if file_extension == '.txt':
# 		# leave .txt files as is
# 		converted_content = file_content
# 		print("txt to txt")
# 	elif file_extension == '.docx':
# 		# convert .docx to .txt
# 		converted_content = convert_docx_to_txt(file_content)
# 		print("docx to txt")
# 	else:
# 		# unsupported file type
# 		print(f"Unsupported file type: {file_name}")
# 		# TO DO: deal with unsupported file type if they somehow got passed in
	
# 	return converted_content