from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
    return render(request, 'verify.html')

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
        documents_data = [{'title': doc.title} for doc in documents]
        return JsonResponse(documents_data, safe=False)
    except Profile.DoesNotExist:
        return JsonResponse([], safe=False)