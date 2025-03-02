from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StudentProfile
from django.db import transaction
from django.core.exceptions import ValidationError
from utils.widgets import CloudflareTurnstileWidget  # Import the widget
from django.contrib.auth.forms import AuthenticationForm
from utils.forms import TurnstileMixin

class CustomLoginForm(TurnstileMixin, AuthenticationForm):
    pass

class StudentRegistrationForm(UserCreationForm):

    captcha = forms.CharField(widget=CloudflareTurnstileWidget())

    first_name = forms.CharField(
        max_length=255,
        required=True,
        label='First Name',
        error_messages={
            'required': 'First Name is required.',
            'max_length': 'First Name cannot be more than 255 characters.'
        }
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        label='Last Name',
        error_messages={
            'required': 'Last Name is required.',
            'max_length': 'Last Name cannot be more than 255 characters.'
        }
    )
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    terms = forms.BooleanField(
        required=True,
        label='I agree to the Terms and Conditions',
        error_messages={
            'required': 'You must accept the Terms and Conditions to register.'
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')
        error_messages = {
            'password2': {
                'password_mismatch': 'Confirm Password does not match the Main Password.',
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Main Password'
        self.fields['password2'].label = 'Confirm Password'
        self.fields['password1'].help_text = 'Password must be at least 6 characters long and contain at least one number.'

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 6:
            raise ValidationError('Password must be at least 6 characters long.')
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one number.')
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Confirm Password does not match the Main Password.')
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise ValidationError("Phone number should contain only digits.")
        return phone

    def clean_captcha(self):
            import requests
            from django.conf import settings

            captcha_response = self.cleaned_data.get('captcha')
            secret_key = settings.CLOUDFLARE_TURNSTILE_SECRET_KEY
            verify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

            response = requests.post(verify_url, data={
                'secret': secret_key,
                'response': captcha_response,
            })
            result = response.json()

            if not result.get('success'):
                raise forms.ValidationError('Invalid CAPTCHA. Please try again.')

            return captcha_response

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            # The profile will be created by the signal, but we update it with the phone number
            profile, created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': self.cleaned_data['phone']
                }
            )

            if not created:
                # Update existing profile
                profile.phone = self.cleaned_data['phone']
                profile.first_name = user.first_name
                profile.last_name = user.last_name
                profile.save()

        return user
    

class CustomLoginForm(AuthenticationForm):
    # Add Turnstile field
    captcha = forms.CharField(widget=CloudflareTurnstileWidget(), required=True)

    def clean_captcha(self):
        import requests
        from django.conf import settings

        captcha_response = self.cleaned_data.get('captcha')
        secret_key = settings.CLOUDFLARE_TURNSTILE_SECRET_KEY
        verify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

        response = requests.post(verify_url, data={
            'secret': secret_key,
            'response': captcha_response,
        })
        result = response.json()

        if not result.get('success'):
            raise forms.ValidationError('Invalid CAPTCHA. Please try again.')

        return captcha_response