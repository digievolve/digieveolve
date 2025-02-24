# services/views.py
from django.shortcuts import render

def service_list(request):
    return render(request, 'services/list.html')

def digital_transformation(request):
    return render(request, 'services/digital_transformation.html')

def consulting(request):
    return render(request, 'services/consulting.html')

def development(request):
    return render(request, 'services/development.html')