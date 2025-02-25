# services/views.py
from django.shortcuts import render

def service_list(request):
    return render(request, 'pages/services/list.html')

def digital_transformation(request):
    return render(request, 'pages/services/digital_transformation.html')  # Updated path

def consulting(request):
    return render(request, 'pages/services/consulting.html')

def development(request):
    return render(request, 'pages/services/development.html')

def automation(request):
    return render(request, 'pages/services/automation.html')

def research(request):
    return render(request, 'pages/services/research.html')

def career(request):
    return render(request, 'pages/services/career.html')

def global_talent(request):
    return render(request, 'pages/services/global_talent.html')