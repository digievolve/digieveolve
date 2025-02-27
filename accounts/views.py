# Python standard library imports
from datetime import timedelta

# Django imports
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

# Local application imports
from .forms import StudentRegistrationForm
from .models import Activity, Certificate, Course, Enrollment, StudentProfile

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')  # Changed from student:dashboard

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Get the next URL or default to accounts dashboard
                next_url = request.GET.get('next', reverse('accounts:dashboard'))
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please check your username and password and try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'page_title': 'Login to Your Account'
    })

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # This already creates the profile
            login(request, user)
            messages.success(request, "Welcome to Digievolve! Your account has been created successfully.")
            return redirect('accounts:profile')
        else:
            # Improve error display
            if form.errors:
                for field in form.errors:
                    for error in form.errors[field]:
                        messages.error(request, f"{field}: {error}")
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'page_title': 'Create Your Student Account'
    })

@login_required
def dashboard_view(request):
    try:
        # Get the student profile
        student = StudentProfile.objects.get(user=request.user)

        # Get enrolled courses
        enrolled_courses = Enrollment.objects.filter(student=student).select_related('course')

        # Get certificates
        certificates = Certificate.objects.filter(student=student)

        # Calculate overall progress
        total_courses = enrolled_courses.count()
        if total_courses > 0:
            # Calculate completed modules across all courses
            completed_modules = Enrollment.objects.filter(
                student=student
            ).aggregate(
                completed=Sum('completed_modules'),
                total=Sum('course__total_modules')
            )

            if completed_modules['total'] > 0:
                progress_percentage = int((completed_modules['completed'] or 0) / completed_modules['total'] * 100)
            else:
                progress_percentage = 0
        else:
            progress_percentage = 0

        # Get recent activities (last 30 days)
        recent_activities = Activity.objects.filter(
            student=student,
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).order_by('-timestamp')[:5]

        # Get recommended courses (courses not enrolled in)
        recommended_courses = Course.objects.exclude(
            id__in=enrolled_courses.values_list('course_id', flat=True)
        ).order_by('?')[:3]  # Random selection of 3 courses

        context = {
            'student': student,
            'enrolled_courses': enrolled_courses,
            'certificates': certificates,
            'progress_percentage': progress_percentage,
            'recent_activities': recent_activities,
            'recommended_courses': recommended_courses,
        }

        return render(request, 'accounts/dashboard.html', context)

    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact support.")
        return redirect('accounts:login')
     

@login_required
def profile_view(request):
    try:
        student = StudentProfile.objects.get(user=request.user)

        # Get enrolled courses
        enrolled_courses = Enrollment.objects.filter(student=student).select_related('course')

        # Calculate completed courses count
        completed_courses_count = enrolled_courses.filter(is_completed=True).count()

        # Get certificates
        certificates = Certificate.objects.filter(student=student)

        context = {
            'student': student,
            'enrolled_courses': enrolled_courses,
            'enrolled_courses_count': enrolled_courses.count(),
            'completed_courses_count': completed_courses_count,
            'certificates': certificates,
            'certificates_count': certificates.count(),
        }

        return render(request, 'accounts/profile.html', context)

    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact support.")
        return redirect('accounts:login')

@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html', {
        'page_title': 'Account Settings'
    })