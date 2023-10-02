from django.db import models
from django.contrib.auth.models import User
from django.http import HttpRequest

class Profile(models.Model):
    """ Profile Table """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    

class Document(models.Model):
    """ Document Table """

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    
    def __str__(self):
        return self.title

# Non-class function to check profile stuff
def safe_profile_select(request: HttpRequest, profile:Profile = None) -> Profile|None:
    """Allows querying and selection of current profile based on a request
    Returns the currently selected Profile or None, but only if it
    exists, is a valid profile and belongs to the user asking for it"""

    # Set the profile to operate on
    profile = request.session.get('profile_cur') if not profile else profile
    if not isinstance(profile, Profile): return None  # No valid reference to a current profile anywhere

    # Catch when a profile doesn't exist or doesn't belong to the user
    if not Profile.objects.filter(user=request.user, id=profile.id).exists():
        profile = None
    
    # No profile? Remove the session variable
    if profile:
        request.session['profile_cur'] = profile
    else:
        if 'profile_cur' in request.session:
            request.session.pop('profile_cur')
    
    return profile  # Will be None if profile doesn't pass