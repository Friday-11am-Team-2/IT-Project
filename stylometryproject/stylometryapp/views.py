from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

import json
import random

from .forms import DocumentForm
from .models import *


def home_page_view(request):
    return render(request, 'index.html')


def about_page_view(request):
    return render(request, 'about.html')


def profile_page_view(request):
    profiles = Profile.objects.all()
    return render(request, 'profile.html', {'profiles': profiles})


def verify_page_view(request):
    profiles = Profile.objects.all()
    return render(request, 'verify.html', {'profiles': profiles})


@csrf_exempt  # Use this decorator if you want to bypass CSRF protection for this view (for simplicity)
def create_profile(request):
    if request.method == 'POST':
        new_profile_name = request.POST.get('name')

        # Create a new profile
        profile = Profile(name=new_profile_name)
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


def get_profile_name(request, profile_id):
    try:
        profile = Profile.objects.get(pk=profile_id)
        return JsonResponse({'name': profile.name})
    except Profile.DoesNotExist:
        return JsonResponse({'name': 'None'})


def get_documents(request, profile_id):
    try:
        profile = Profile.objects.get(pk=profile_id)
        documents = Document.objects.filter(profile=profile)
        documents_data = [{'id': document.id, 'title': document.title} for document in documents]
        return JsonResponse(documents_data, safe=False)
    except Profile.DoesNotExist:
        return JsonResponse([], safe=False)


@csrf_exempt 
def add_profile_docs(request):

    if request.method == "POST":
        try:
            # Get the JSON data from the request
            data = json.loads(request.body)

            # Extract the profile_id and file_data from the JSON data
            profile_id = data.get("profile_id")
            names = data.get("file_names")
            texts = data.get("file_contents")

            # Check if the profile exists (you can add more error handling here)
            profile = Profile.objects.get(pk=profile_id)

            # Create and save ProfileDocument instances for each file
            for i in range(len(names)):
                Document.objects.create(profile=profile, title=names[i], text=texts[i])

            # Return a success response
            return JsonResponse({"message": "Documents added successfully"}, status=201)
        

        except Exception as e:
            # Handle exceptions and return an error response
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt 
def delete_profile(request):
    if request.method == "POST" and request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        profile_id = request.POST.get("profile_id")
        try:
            profile = Profile.objects.get(id=profile_id)
            profile.delete()
            return JsonResponse({"message": "Profile deleted successfully"})
        except Profile.DoesNotExist:
            return JsonResponse({"error": "Profile not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)
    

@csrf_exempt 
def edit_profile(request, profile_id):
    if request.method == "POST" and request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        new_name = request.POST.get("profile_name")
        try:
            profile = Profile.objects.get(id=profile_id)
            profile.name = new_name
            profile.save()
            return JsonResponse({"message": "Profile updated successfully"})
        except Profile.DoesNotExist:
            return JsonResponse({"error": "Profile not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)
    

@csrf_exempt
def delete_document(request, document_id):
    try:
        document = Document.objects.get(id=document_id)
        document.delete()
        return JsonResponse({'message': 'Document deleted successfully'})
    except Document.DoesNotExist:
        return JsonResponse({'error': 'Document not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred while deleting the document'}, status=500)


@csrf_exempt
def run_verification(request):
    if request.method == "POST":
        try:
            # Get the JSON data from the request
            data = json.loads(request.body)

            # Extract the profile_id and file_data from the JSON data
            profile_id = data.get("profile_id")
            names = data.get("file_names")
            texts = data.get("file_contents")

            # Check if the profile exists (you can add more error handling here)
            profile = Profile.objects.get(pk=profile_id)

            # Get the documents for the profile
            documents = Document.objects.filter(profile=profile)
            if (len(documents) == 0):
                print("No documents found for the profile")
                return JsonResponse({"error": "No documents found for the profile"}, status=400)


            # RUN ALGORITHM HERE
            # for now make random number
            value = round(random.uniform(0, 1), 2)

            # Return a success response
            return JsonResponse({"message": "Verification Successful", "result": value}, status=201)
        

        except Exception as e:
            # Handle exceptions and return an error response
            return JsonResponse({"error": str(e)}, status=400)