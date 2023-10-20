from django.shortcuts import render, redirect, reverse
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect, HttpRequest
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

import json
import random

from stylometry import StyloNet, TextAnalytics, strip_text

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
    cur_profile_name = str(cur_profile.name) if cur_profile else "None"
    cur_profile_id = str(cur_profile.id) if cur_profile else -1

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

    cur_profile_name = str(cur_profile.name) if cur_profile else "None"
    cur_profile_id = str(cur_profile.id) if cur_profile else -1

    return render(request, 'verify.html', {
        'profiles': profiles,
        'profile_name': cur_profile_name,
        'profile_id': cur_profile_id
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
        documents_data = [{'id': document.id, 'title': document.title}
                          for document in documents]

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

            # Handle file type conversion
            for i in range(len(names)):
                texts[i] = convert_file(names[i], texts[i])

            # Check if the profile exists (you can add more error handling here)
            profile = Profile.objects.get(pk=profile_id, user=request.user)

            # Create and save ProfileDocument instances for each file
            for i in range(len(names)):
                Document.objects.create(
                    profile=profile, title=names[i], text=texts[i])

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
def run_verification(request:HttpRequest) -> JsonResponse:
    """ Runs the verification algorithm """

    if request.method == "POST":
        try:
            # Get the JSON data from the request
            data = json.loads(request.body)

            # Extract the profile_id and file_data from the JSON data
            profile_id = data.get("profile_id")
            name = data.get("file_names")
            text = data.get("file_contents")

            # Handle file type conversion
            text[0] = convert_file(name[0], text[0])

            # Check if the profile exists (you can add more error handling here)
            profile = Profile.objects.get(pk=profile_id, user=request.user)

            # Get the documents for the profile
            documents = Document.objects.filter(profile=profile)
            if (len(documents) == 0):
                print("No documents found for the profile")
                raise Exception("No documents found for the profile")

            # RUN ALGORITHM #
            text_data = {
                'known': [document.text for document in documents],
                'unknown': [text]
            }

            model = get_stylonet()

            result, score = model.predict(text_data)
            score = round(score, 3)

            # Cache the most recent unknown file uploaded
            request.session['prev_unknown'] = (strip_text(text_data['unknown']))

            # Return a success response
            return JsonResponse({
                "message": "Verification Successful",
                "result": True if result else False,
                "score": str(score),
            }, status=201)

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
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/home/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def text_analytics(request:HttpRequest) -> JsonResponse:
    """Provide analytics on a profile or uploaded file"""
    try:
        if request.GET.get('p'):
            profile = Profile.objects.get(pk=request.GET.get('p'), user=request.user)

            documents = Document.objects.filter(profile=profile)
            if not documents:
                raise AttributeError('No documents found for the profile')

            analysis = TextAnalytics([ doc.text for doc in documents ])
        
        elif request.GET.get('f'):
            data = json.loads(request.body)
            target = request.GET.get('f')

            names = data['file_names']
            text = data['file_contents']

            if not target in names:
                raise AttributeError(f"File {target} not found!")
            
            converted = convert_file(target, text.index[target])

            analysis = TextAnalytics(converted)

        elif request.GET.get('l'):
            if not 'prev_unknown' in request.session:
                raise AttributeError("Previous text not found")
            
            analysis = TextAnalytics(request.session['prev_unknown'])

        else:
            raise ValueError("Empty request!")
        

        sentence_info = analysis.sentence_length_distrib()
        jsonify_float = lambda x: str(round(x, 3))

        return JsonResponse({
            "rare_words": jsonify_float(analysis.rare_words_freq()),
            "long_words": jsonify_float(analysis.long_words_freq()),
            "sentence_avg": jsonify_float(analysis.sentence_length_avg()),
            "sentence_below": str(sentence_info[0]),
            "sentence_equal": str(sentence_info[1]),
            "sentence_above": str(sentence_info[2]),
            "word_len_avg": str(analysis.word_length_avg()),
            "word_count": jsonify_float(analysis.word_count())
        }, status=201)
    except (ValueError, AttributeError) as e:
        if __debug__: print(f"analytics err: {e}")
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        if __debug__: print(f"general err: {type(e)}: {e}")
        return JsonResponse({"error": "Internal Server Error"}, status=400)