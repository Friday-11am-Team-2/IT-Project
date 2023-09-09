from django.apps import AppConfig
from .utils import getStyloNet

class StylometryappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stylometryapp'

    def ready(self):
        getStyloNet()  # Run get to force the Stylometry Model initialization