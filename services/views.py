# services/views.py
from django.http import Http404
from django.shortcuts import render
from .services_data import services_data



def service_list(request):
    return render(request, 'pages/services/list.html')

def service_detail(request, service_slug):
    service = services_data.get(service_slug)
    if not service:
        raise Http404("Service not found")

    context = {
        'service': service,
        'service_slug': service_slug
    }
    return render(request, 'pages/service_detail.html', context)

# def digital_transformation(request):
#     return render(request, 'pages/services/digital_transformation.html')

# def consulting(request):
#     return render(request, 'pages/services/consulting.html')

# def development(request):
#     return render(request, 'pages/services/development.html')

# def automation(request):
#     return render(request, 'pages/services/automation.html')

# def research(request):
#     return render(request, 'pages/services/research.html')

# def career(request):
#     return render(request, 'pages/services/career.html')

# def global_talent(request):
#     return render(request, 'pages/services/global_talent.html')