# courses/urls.py
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('my-courses/', views.enrolled_courses, name='enrolled_courses'),
    path('certificates/', views.certificate_list, name='certificate_list'),
    path('<str:course_slug>/', views.course_detail, name='detail'),
    path('<str:course_slug>/module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('<str:course_slug>/module/<int:module_id>/quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    path('<str:course_slug>/initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('verify-payment/<str:reference>/', views.verify_payment, name='verify_payment'),
]