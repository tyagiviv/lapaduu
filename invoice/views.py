from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def generate_invoice(request):
    return render(request, 'generator.html')
