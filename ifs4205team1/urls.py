"""ifs4205team1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
# from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.views.static import serve

from ifs4205team1 import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('patient/', include('patientlogin.urls')),
    path('patient/', include('patientrecords.urls')),
    path('patient/', include('patienthealthcare.urls')),
    path('healthcare/', include('healthcarelogin.urls')),
    path('healthcare/', include('healthcarepatients.urls')),
    path('researcher/', include('researcherlogin.urls')),
    path('researcher/', include('researcherquery.urls')),
    path('researcher/', include('researcheranonymise.urls')) # Change to admin
] 

if settings.DEBUG:
  urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
