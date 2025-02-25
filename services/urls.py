# services/urls.py
from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('digital-transformation/', views.digital_transformation, name='digital_transformation'),
    path('consulting/', views.consulting, name='consulting'),
    path('development/', views.development, name='development'),
    path('automation/', views.automation, name='automation'),
    path('research/', views.research, name='research'),
    path('career/', views.career, name='career'),
    path('global_talent/', views.global_talent, name='global_talent'),
    
]