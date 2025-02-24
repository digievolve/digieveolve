# services/urls.py
from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('digital-transformation/', views.digital_transformation, name='digital_transformation'),
    path('consulting/', views.consulting, name='consulting'),
    path('development/', views.development, name='development'),
]