# courses/urls.py
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('digital-marketing/', views.digital_marketing, name='digital_marketing'),
    path('web-development/', views.web_development, name='web_development'),
]