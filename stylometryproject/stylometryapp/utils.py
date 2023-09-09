from django.conf import settings
import Stylometry

### Stylometry Model Utils ###
stylometry_model: Stylometry.StyloNet|None = None

def getStyloNet() -> Stylometry.StyloNet:
	"""Initialize or return the existing instance of the StyloNet object"""
	global stylometry_model

	# Initialize if not already, otherwise just return existing
	if stylometry_model is None:
		stylometry_model = Stylometry.StyloNet(settings.STYLOMETRY_DIR, settings.STYLOMETRY_MATCH_THRESHOLD)
		print(f"Initialized Stylometry Model at {id(stylometry_model)}")

	return stylometry_model