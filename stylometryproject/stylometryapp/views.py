from django.shortcuts import render

def home_page_view(request):
    return render(request, 'index.html')

def about_page_view(request):
    return render(request, 'about.html')

def profile_page_view(request):
    return render(request, 'profile.html')

def verify_page_view(request):
    return render(request, 'verify.html')