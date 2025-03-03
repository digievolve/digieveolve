from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('', views.resource_list, name='list'),
    # This matches your ResourceCategory.get_absolute_url
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    # Add this to match what's in your template
    path('category/<slug:category_slug>/', views.category_detail, name='category'),
    # Add this for individual resources
    path('<slug:slug>/', views.resource_detail, name='detail'),
]