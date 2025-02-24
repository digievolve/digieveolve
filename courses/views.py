# courses/views.py
from django.shortcuts import render

def course_list(request):
    return render(request, 'courses/list.html')

def digital_marketing(request):
    return render(request, 'courses/digital_marketing.html')

def web_development(request):
    return render(request, 'courses/web_development.html')