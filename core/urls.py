"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import include, re_path
from .docusign_configs import * 

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^docusign_signature/$', docusign_signature, name='docusign_signature'),
    re_path(r'^sign_completed/$', sign_completed, name='sign_completed'),
    path('get_envelope_status/<str:envelope_id>', get_envelope_status, name='get_envelope_status'),

]
