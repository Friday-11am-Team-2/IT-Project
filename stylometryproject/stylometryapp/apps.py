from django.apps import AppConfig
from .utils import stylonet_preload

class StylometryappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stylometryapp'

    def ready(self):
        stylonet_preload()  # Run get to force the Stylometry Model initialization