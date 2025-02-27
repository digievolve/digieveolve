from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Certificate, Enrollment
from accounts.models import StudentProfile

@login_required(login_url='accounts:login')
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/list.html', {'courses': courses})

@login_required(login_url='accounts:login')
def course_detail(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    try:
        enrollment = Enrollment.objects.get(student__user=request.user, course=course)
    except Enrollment.DoesNotExist:
        enrollment = None
    return render(request, 'courses/detail.html', {
        'course': course,
        'enrollment': enrollment
    })

@login_required(login_url='accounts:login')
def enrolled_courses(request):
    enrollments = Enrollment.objects.filter(
        student__user=request.user
    ).select_related('course')
    return render(request, 'courses/enrolled_courses.html', {'enrollments': enrollments})

@login_required(login_url='accounts:login')
def certificate_list(request):
    # Assuming you have a way to get the user's certificates
    certificates = Certificate.objects.filter(student__user=request.user)
    return render(request, 'courses/certificate_list.html', {'certificates': certificates})

@login_required(login_url='accounts:login')
def certificate_detail(request, certificate_id):
    certificate = get_object_or_404(
        Certificate,
        id=certificate_id,
        student__user=request.user
    )
    return render(request, 'courses/certificate_detail.html', {'certificate': certificate})