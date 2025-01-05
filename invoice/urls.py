# invoice/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('generate_invoice/', views.generate_invoice, name='generate_invoice'),
    path('get_next_invoice_number/', views.get_next_invoice_number_view, name='get_next_invoice_number'),
    # Updated view
]
