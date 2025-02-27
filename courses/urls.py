# courses/urls.py
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('my-courses/', views.enrolled_courses, name='enrolled_courses'),
    path('certificates/', views.certificate_list, name='certificate_list'),
    path('<str:course_slug>/', views.course_detail, name='detail'),
]