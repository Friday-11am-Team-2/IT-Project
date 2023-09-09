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