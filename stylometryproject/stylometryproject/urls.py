"""
URL configuration for stylometryproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from stylometryapp.views import *

urlpatterns = [
    # Pages
    path('admin/', admin.site.urls),
    path('', home_page_view),
    path('home/', home_page_view),
    path('about/', about_page_view),
    path('profile/', profile_page_view),
    path('verify/', verify_page_view),

    # Create profile
    path('create_profile/', create_profile, name='create_profile'),
    
    # URL pattern for fetching the profile name
    path('get_profile_name/<int:profile_id>/', get_profile_name, name='get_profile_name'),

    # URL pattern for fetching documents by profile
    path('get_documents/<int:profile_id>/', get_documents, name='get_documents'),

    # Add docs to pofile
    path('add_profile_docs/', add_profile_docs, name='add_profile_docs'),
] 
