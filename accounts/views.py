# Python standard library imports
from datetime import timedelta, timezone

# Django imports
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse
import requests

from digievolve import settings


# Local application imports
from .models import Activity, StudentProfile
from courses.models import Certificate, Course, Enrollment  # Import from courses app
from django.db import models  # Add this import for aggregation
from .forms import StudentRegistrationForm, CustomLoginForm  # Add
import logging

logger = logging.getLogger(__name__)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        # Create a copy of POST data that we can modify
        post_data = request.POST.copy()

        # Get the Turnstile token
        token = request.POST.get('cf-turnstile-response')

        # Add the token to the form data with the correct field name
        if token:
            post_data['cf_turnstile_response'] = token

        # Initialize the form with the modified POST data
        form = StudentRegistrationForm(post_data)

        # Validate Cloudflare Turnstile separately from form validation
        if not token:
            messages.error(request, "Please complete the security check.")
            return render(request, 'accounts/register.html', {'form': form})

        # Verify the token with Cloudflare
        secret_key = settings.CLOUDFLARE_TURNSTILE_SECRET_KEY
        data = {
            'secret': secret_key,
            'response': token,
            'remoteip': request.META.get('REMOTE_ADDR')
        }

        try:
            response = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=data)
            result = response.json()

            if not result.get('success', False):
                logger.error(f"Turnstile verification failed: {result}")
                messages.error(request, "Security check failed. Please try again.")
                return render(request, 'accounts/register.html', {'form': form})
        except Exception as e:
            logger.error(f"Turnstile verification error: {e}")
            messages.error(request, "Error verifying security check. Please try again.")
            return render(request, 'accounts/register.html', {'form': form})

        # If Turnstile validation passed, proceed with form validation
        if form.is_valid():
            try:
                # Save the user and log them in
                user = form.save()
                login(request, user)
                messages.success(request, "Welcome to DigiEvolve! Your account has been created successfully.")
                return redirect('accounts:profile')
            except Exception as e:
                logger.error(f"Registration error: {e}")
                messages.error(request, f"An error occurred during registration: {e}")
        else:
            # Display form errors as messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        # Initialize an empty form for GET requests
        form = StudentRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'page_title': 'Create Your Student Account'
    })

def login_view(request):
    if request.method == 'POST':
        # Create a copy of POST data that we can modify
        post_data = request.POST.copy()

        # Get the Turnstile token
        token = request.POST.get('cf-turnstile-response')

        # Add the token to the form data with the correct field name
        if token:
            post_data['cf_turnstile_response'] = token

        # Initialize form with request and modified POST data
        form = CustomLoginForm(request=request, data=post_data)

        # Validate Cloudflare Turnstile separately from form validation
        if not token:
            messages.error(request, "Please complete the security check.")
            return render(request, 'accounts/login.html', {'form': form})

        # Verify the token with Cloudflare
        secret_key = settings.CLOUDFLARE_TURNSTILE_SECRET_KEY
        data = {
            'secret': secret_key,
            'response': token,
            'remoteip': request.META.get('REMOTE_ADDR')
        }

        try:
            response = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=data)
            result = response.json()

            if not result.get('success', False):
                logger.error(f"Turnstile verification failed: {result}")
                messages.error(request, "Security check failed. Please try again.")
                return render(request, 'accounts/login.html', {'form': form})
        except Exception as e:
            logger.error(f"Turnstile verification error: {e}")
            messages.error(request, "Error verifying security check. Please try again.")
            return render(request, 'accounts/login.html', {'form': form})

        # If Turnstile validation passed, proceed with form validation
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = request.POST.get('remember_me')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                if not remember_me:
                    request.session.set_expiry(0)

                # Record login activity
                try:
                    profile = StudentProfile.objects.get(user=user)
                    Activity.objects.create(
                        student=profile,
                        activity_type='login',
                        description=f"Logged in at {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                    )
                except Exception as e:
                    # Just log the error, don't interrupt the login process
                    logger.error(f"Error recording login activity: {e}")

                return redirect('accounts:dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            # Display form errors as messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form})



@login_required(login_url='accounts:login')
def dashboard_view(request):
    # Get student profile
    student_profile = StudentProfile.objects.get(user=request.user)

    # Get enrolled courses
    enrolled_courses = Enrollment.objects.filter(
        student=student_profile
    ).select_related('course')

    # Get certificates
    certificates = Certificate.objects.filter(
        student=student_profile
    ).select_related('course')

    # Calculate progress percentage
    total_courses = enrolled_courses.count()
    completed_courses = enrolled_courses.filter(is_completed=True).count()
    progress_percentage = (completed_courses / total_courses * 100) if total_courses > 0 else 0

    # Get recent activities
    recent_activities = Activity.objects.filter(
        student=student_profile
    ).select_related('course').order_by('-timestamp')[:5]

    # Get recommended courses
    enrolled_course_ids = enrolled_courses.values_list('course_id', flat=True)
    recommended_courses = Course.objects.exclude(
        id__in=enrolled_course_ids
    ).order_by('?')[:3]  # Random selection of 3 courses

    context = {
        'student': student_profile,
        'enrolled_courses': enrolled_courses,
        'certificates': certificates,
        'progress_percentage': round(progress_percentage, 1),
        'recent_activities': recent_activities,
        'recommended_courses': recommended_courses,
    }

    return render(request, 'accounts/dashboard.html', context)


@login_required
def courses_view(request):
    student_profile = StudentProfile.objects.get(user=request.user)
    enrolled_courses = Enrollment.objects.filter(student=student_profile).select_related('course')

    context = {
        'enrolled_courses': enrolled_courses,
    }

    return render(request, 'accounts/courses.html', context)

@login_required
def certificates_view(request):
    student_profile = StudentProfile.objects.get(user=request.user)
    certificates = Certificate.objects.filter(student=student_profile).select_related('course')

    context = {
        'certificates': certificates,
    }

    return render(request, 'accounts/certificates.html', context)


@login_required
def profile_view(request):
    try:
        student = StudentProfile.objects.get(user=request.user)

        # Get enrolled courses
        enrolled_courses = Enrollment.objects.filter(student=student).select_related('course')

        # Calculate completed courses count
        completed_courses_count = enrolled_courses.filter(is_completed=True).count()  # Change is_completed to completed

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
    try:
        student = StudentProfile.objects.get(user=request.user)

        if request.method == 'POST':
            form_type = request.POST.get('form_type')

            if form_type == 'profile_info':
                # Handle profile information update
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                bio = request.POST.get('bio')

                # Update user information
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.email = email
                request.user.save()

                # Update student profile information
                student.phone = phone
                student.bio = bio
                student.save()

                messages.success(request, "Your profile information has been updated successfully.")

            elif form_type == 'password_change':
                # Handle password change
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')

                if password1 and password2:
                    if password1 == password2:
                        request.user.set_password(password1)
                        request.user.save()
                        # Re-authenticate user to prevent logout after password change
                        login(request, request.user)
                        messages.success(request, "Your password has been changed successfully.")
                    else:
                        messages.error(request, "Passwords do not match.")
                else:
                    messages.error(request, "Please enter both password fields.")

            return redirect('accounts:settings')

        return render(request, 'accounts/settings.html', {
            'student': student,
            'page_title': 'Account Settings'
        })

    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact support.")
        return redirect('accounts:dashboard')



def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('core:home')


# For development/testing
def validate_turnstile(request):
    """Validate the Cloudflare Turnstile token"""
    # Get the token from the request
    token = request.POST.get('cf-turnstile-response')

    # If using test key, accept any response
    if settings.DEBUG:
        return True

    # For production, verify with Cloudflare
    if not token:
        return False

    # Verify the token with Cloudflare
    secret_key = "YOUR_SECRET_KEY"  # Add to settings.py
    data = {
        'secret': secret_key,
        'response': token,
        'remoteip': request.META.get('REMOTE_ADDR')
    }

    try:
        response = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=data)
        result = response.json()
        return result.get('success', False)
    except Exception:
        # Log the exception
        return False