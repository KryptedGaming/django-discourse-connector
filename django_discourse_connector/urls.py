from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('sso/callback', views.sso_callback,
         name="django-discord-connector-sso-callback"),
]
