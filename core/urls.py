from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('resources/', views.resources, name='resources'),
    path('training-programs/', views.training_programs, name='training_programs'),
    path('services/', views.services_page, name='services'),
    path('services/<str:slug>/', views.service_detail, name='service_detail'),
    path('training-programs/<str:slug>/', views.training_detail, name='training_detail'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
]