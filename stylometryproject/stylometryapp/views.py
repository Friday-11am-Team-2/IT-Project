from django.shortcuts import render, redirect, reverse
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

import json
import random
from stylometry import StyloNet

from .forms import DocumentForm
from .models import *
from .utils import stylonet_preload, get_stylonet, convert_file, safe_profile_select

# Dispatch preloader thread now that application has loaded up
stylonet_preload()

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

    # Grab currently select profile from session, "None" otherwise
    cur_profile = safe_profile_select(request)
    cur_profile_name = cur_profile.name if cur_profile else "None"
    cur_profile_id = cur_profile.id if cur_profile else -1

    return render(request, 'profile.html', {
        'profiles': profiles,
        'profile_name': cur_profile_name,
        'profile_id': cur_profile_id
    })


@login_required
def verify_page_view(request):
    """ Renders the verify page """
    current_user = request.user
    profiles = Profile.objects.filter(user=current_user)

    # Grab currently select profile from session, "None" otherwise
    cur_profile = safe_profile_select(request)

    cur_profile_name = cur_profile.name if cur_profile else "None"
    cur_profile_id = cur_profile.id if cur_profile else -1

    return render(request, 'verify.html', {
        'profiles': profiles,
        'profile_name': cur_profile_name,
        'profile_id' : cur_profile_id
    })


@login_required
@csrf_protect
def create_profile(request):
    """ Creates a new profile """

    if request.method == 'POST':
        new_profile_name = request.POST.get('name')

        # Create a new profile
        profile = Profile(name=new_profile_name, user=request.user)
        profile.save()

        # Set the newly created profile as the selected
        safe_profile_select(request, profile)

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

        # Set this as the selected profile (assume getting docs mean's selecting)
        safe_profile_select(request, profile)

        return JsonResponse(documents_data, safe=False)
    except Profile.DoesNotExist:
        return JsonResponse([], safe=False)


@login_required
@csrf_protect
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

            # Handle file type conversion (TO DO: upload seems to corrupt docx files)
            # for i in range(len(names)):
            #     print(i)
            #     texts[i] = convert_file(names[i], texts[i])

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
@csrf_protect
def delete_profile(request):
    """ Deletes a profile """

    if request.method == "POST" and request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        profile_id = request.POST.get("profile_id")
        try:
            profile = Profile.objects.get(id=profile_id, user=request.user)
            profile.delete()

            # Clear selected profile against the deleted one
            if 'selected_profile' in request.session:
                if profile.id == request.session['selected_profile']:
                    # Remove if they're the same
                    request.session.pop('selected_profile')

            return JsonResponse({"message": "Profile deleted successfully"})
        except Profile.DoesNotExist:
            return JsonResponse({"error": "Profile not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)
    

@login_required
@csrf_protect
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
@csrf_protect
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
@csrf_protect
def run_verification(request):
    """ Runs the verification algorithm """

    if request.method == "POST":
        try:
            # Get the JSON data from the request
            data = json.loads(request.body)

            # Extract the profile_id and file_data from the JSON data
            profile_id = data.get("profile_id")
            name = data.get("file_names")
            text = data.get("file_contents")

            # Handle file type conversion (TO DO: upload seems to corrupt docx files)
            # text[0] = convert_file(name[0], text[0])
            
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
                'unknown': [ text ]
            }

            model = get_stylonet()

            value = round(model.score(text_data), 3)

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