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

def automation(request):
    return render(request, 'services/automation.html')

def research(request):
    return render(request, 'services/research.html')

def career(request):
    return render(request, 'services/career.html')

def global_talent(request):
    return render(request, 'services/global_talent.html')