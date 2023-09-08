from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    """ Form for the Document model """

    class Meta:
        model = Document
        fields = ['profile', 'title', 'text']