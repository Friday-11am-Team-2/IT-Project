from django.shortcuts import render, redirect, reverse
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

import json
import random

from .forms import DocumentForm
from .models import *

from Stylometry import StyloNet
stylometry_model = StyloNet("model_storage")

# TO DO - remove CSRF decorators
def home_page_view(request):
    """ Renders the home page """
    return render(request, 'index.html')


def about_page_view(request):
    """ Renders the about page """
    return render(request, 'about.html')


@login_required
def profile_page_view(request):
    """ Renders the profile page """
    current_user = request.user
    profiles = Profile.objects.filter(user=current_user)
    return render(request, 'profile.html', {'profiles': profiles})


@login_required
def verify_page_view(request):
    """ Renders the verify page """
    current_user = request.user
    profiles = Profile.objects.filter(user=current_user)
    return render(request, 'verify.html', {'profiles': profiles})


@login_required
@csrf_exempt
def create_profile(request):
    """ Creates a new profile """

    if request.method == 'POST':
        new_profile_name = request.POST.get('name')

        # Create a new profile
        profile = Profile(name=new_profile_name, user=request.user)
        profile.save()

        # Return the newly created profile data as JSON
        data = {
            'id': profile.id,
            'name': profile.name,
        }
        return JsonResponse(data)

    # Handle other HTTP methods if needed
    else:
        # Handle other HTTP methods or return an error
        return JsonResponse({'error': 'Invalid method'})


@login_required
def get_profile_name(request, profile_id):
    """ Returns the name of the profile with the given ID """

    try:
        profile = Profile.objects.get(pk=profile_id, user=request.user)
        return JsonResponse({'name': profile.name})
    except Profile.DoesNotExist:
        return JsonResponse({'name': 'None'})


@login_required
def get_documents(request, profile_id):
    """ Returns the documents for the profile with the given ID """

    try:
        profile = Profile.objects.get(pk=profile_id, user=request.user)
        documents = Document.objects.filter(profile=profile)
        documents_data = [{'id': document.id, 'title': document.title} for document in documents]
        return JsonResponse(documents_data, safe=False)
    except Profile.DoesNotExist:
        return JsonResponse([], safe=False)


@login_required
@csrf_exempt 
def add_profile_docs(request):
    """ Adds documents to a profile """

    if request.method == "POST":
        try:
            # Get the JSON data from the request
            data = json.loads(request.body)

            # Extract the profile_id and file_data from the JSON data
            profile_id = data.get("profile_id")
            names = data.get("file_names")
            texts = data.get("file_contents")

            # Check if the profile exists (you can add more error handling here)
            profile = Profile.objects.get(pk=profile_id, user=request.user)

            # Create and save ProfileDocument instances for each file
            for i in range(len(names)):
                Document.objects.create(profile=profile, title=names[i], text=texts[i])

            # Return a success response
            return JsonResponse({"message": "Documents added successfully"}, status=201)
        

        except Exception as e:
            # Handle exceptions and return an error response
            return JsonResponse({"error": str(e)}, status=400)


@login_required
@csrf_exempt 
def delete_profile(request):
    """ Deletes a profile """

    if request.method == "POST" and request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        profile_id = request.POST.get("profile_id")
        try:
            profile = Profile.objects.get(id=profile_id, user=request.user)
            profile.delete()
            return JsonResponse({"message": "Profile deleted successfully"})
        except Profile.DoesNotExist:
            return JsonResponse({"error": "Profile not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)
    

@login_required
@csrf_exempt 
def edit_profile(request, profile_id):
    """ Edits a profile's name """

    if request.method == "POST" and request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        new_name = request.POST.get("profile_name")
        try:
            profile = Profile.objects.get(id=profile_id, user=request.user)
            profile.name = new_name
            profile.user = request.user
            profile.save()
            return JsonResponse({"message": "Profile updated successfully"})
        except Profile.DoesNotExist:
            return JsonResponse({"error": "Profile not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)
    

@login_required
@csrf_exempt
def delete_document(request, document_id):
    """ Deletes a document """

    try:
        document = Document.objects.get(id=document_id)
        document.delete()
        return JsonResponse({'message': 'Document deleted successfully'})
    except Document.DoesNotExist:
        return JsonResponse({'error': 'Document not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred while deleting the document'}, status=500)


@login_required
@csrf_exempt
def run_verification(request):
    """ Runs the verification algorithm """

    if request.method == "POST":
        try:
            # Get the JSON data from the request
            data = json.loads(request.body)

            # Extract the profile_id and file_data from the JSON data
            profile_id = data.get("profile_id")
            names = data.get("file_names")
            texts = data.get("file_contents")

            # Check if the profile exists (you can add more error handling here)
            profile = Profile.objects.get(pk=profile_id, user=request.user)

            # Get the documents for the profile
            documents = Document.objects.filter(profile=profile)
            if (len(documents) == 0):
                print("No documents found for the profile")
                return JsonResponse({"error": "No documents found for the profile"}, status=400)


            # RUN ALGORITHM #
            text_data = {
                'known': [ document.text for document in documents ],
                'unknown': [ texts ]
            }

            value = round(stylometry_model.score(text_data), 3)

            # Return a success response
            return JsonResponse({"message": "Verification Successful", "result": str(value)}, status=201)
        

        except Exception as e:
            # Handle exceptions and return an error response
            return JsonResponse({"error": str(e)}, status=400)
        

def register(request):
    """User Registration"""

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username = username, password = password)
            login(request, user)
            return redirect('/home/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})