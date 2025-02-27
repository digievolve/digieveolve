from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='accounts:login')
def course_list(request):
    return render(request, 'courses/list.html')

@login_required(login_url='accounts:login')
def course_detail(request, course_slug):
    return render(request, 'courses/detail.html')