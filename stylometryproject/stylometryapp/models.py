from django.db import models

class Profile(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Document(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    
    def __str__(self):
        return self.title
