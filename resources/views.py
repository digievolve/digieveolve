from django.shortcuts import render, get_object_or_404
from .models import ResourceCategory, Resource

def resource_list(request):
    categories = ResourceCategory.objects.all()
    return render(request, 'resources/resource_list.html', {
        'categories': categories
    })

def category_detail(request, slug=None, category_slug=None):
    # Handle both URL patterns
    if category_slug:
        slug = category_slug

    category = get_object_or_404(ResourceCategory, slug=slug)
    resources = Resource.objects.filter(category=category)

    return render(request, 'resources/category_detail.html', {
        'category': category,
        'resources': resources
    })

def resource_detail(request, slug):
    resource = get_object_or_404(Resource, slug=slug)
    return render(request, 'resources/resource_detail.html', {
        'resource': resource
    })