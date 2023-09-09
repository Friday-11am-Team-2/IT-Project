from django.apps import AppConfig
import stylometryapp.utils as utils

class StylometryappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stylometryapp'

    def ready(self):
        print("Call to get Stylo from AppConfig")
        utils.getStyloNet()  # Run get to force the Stylometry Model initialization