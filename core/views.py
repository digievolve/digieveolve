from django.shortcuts import redirect, render
from .forms import ContactForm
from django.contrib import messages  # Add this import
from .services_data import services_data

def home(request):
    return render(request, 'pages/home.html')


def about(request):
    tools = [
        "Python",
        "BigML",
        "Tableau",
        "Power Platforms",
        "PowerBI",
        "Microsoft Fabrics",
        "Alteryx",
        "SQL",
        "SaS Enterprise Miner",
        "SaS Enterprise Guide",
        "Microsoft Office",
        "SaS Vidya",
        "Looker Studio"
    ]
    return render(request, 'pages/about.html', {'tools': tools})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data
            # Add your email sending logic here
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('core:contact')
    else:
        form = ContactForm()
    return render(request, 'pages/contact.html', {'form': form})


def services_page(request):
    context = {
        'services': services_data
    }
    return render(request, 'pages/services.html', context)

def service_detail(request, slug):
    service = services_data.get(slug)
    if not service:
        return render(request, 'pages/service_not_found.html')

    context = {
        'service': service,
        'slug': slug
    }
    return render(request, 'pages/service_detail.html', context)


# core/views.py
def resources(request):
    resource_categories = {
        'learning_materials': {
            'title': "Learning Materials",
            'icon': "fa-book",
            'items': [
                {
                    'title': "Technical Documentation",
                    'description': "Comprehensive guides for data analytics, science, engineering, and AI tools",
                    'links': ["Python", "BigML", "Tableau", "Power Platforms", "PowerBI", "Microsoft Fabrics"]
                },
                {
                    'title': "Tutorial Libraries",
                    'description': "Step-by-step tutorials for various tools and technologies",
                    'links': ["Alteryx", "SQL", "SAS Enterprise Miner", "SAS Enterprise Guide"]
                },
                {
                    'title': "Practice Datasets",
                    'description': "Real-world datasets for hands-on learning and project work",
                    'links': ["Sample Projects", "Case Studies", "Practice Problems"]
                }
            ]
        },
        # Add other categories similarly
    }
    return render(request, 'pages/resources.html', {'resource_categories': resource_categories})