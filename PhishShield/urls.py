from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('simulator.urls')),  # Directly include simulator URLs
]