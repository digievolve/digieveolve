from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from accounts.models import StudentProfile
from .forms import StudentRegistrationForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required

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
    """
    View for the student dashboard showing enrolled courses, progress, etc.
    """
    try:
        student_profile = request.user.studentprofile
        context = {
            'page_title': 'Student Dashboard',
            'student': student_profile,
            'enrolled_courses': [],  # You'll need to implement this
            'course_progress': {},   # You'll need to implement this
            'certificates': [],      # You'll need to implement this
        }
        return render(request, 'accounts/dashboard.html', context)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact support.")
        return redirect('accounts:login')
    

@login_required
def profile_view(request):
    try:
        student_profile = request.user.studentprofile
    except StudentProfile.DoesNotExist:
        # Create a new profile if it doesn't exist
        student_profile = StudentProfile.objects.create(
            user=request.user,
            full_name=request.user.get_full_name(),
            phone=''
        )

    return render(request, 'accounts/profile.html', {
        'page_title': 'My Profile',
        'student': student_profile
    })

@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html', {
        'page_title': 'Account Settings'
    })