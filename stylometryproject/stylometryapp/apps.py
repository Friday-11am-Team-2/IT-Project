from django.apps import AppConfig
from .utils import getStyloNet

class StylometryappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stylometryapp'

    def ready(self):
        print("Call to get Stylo from AppConfig")
        getStyloNet()  # Run get to force the Stylometry Model initialization