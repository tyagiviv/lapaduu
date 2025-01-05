# invoice/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('generate_invoice/', views.generate_invoice, name='generate_invoice'),
]
