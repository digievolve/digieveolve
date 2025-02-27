from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StudentProfile
from django.db import transaction
from django.core.exceptions import ValidationError

class StudentRegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=255,
        required=True,
        label='Full Name',
        error_messages={
            'required': 'Full Name is required.',
            'max_length': 'Full Name cannot be more than 255 characters.'
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
        fields = ('username', 'email', 'full_name', 'phone', 'password1', 'password2')
        error_messages = {
            'password2': {
                'password_mismatch': 'Confirm Password does not match the Main Password.',
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Main Password'
        self.fields['password2'].label = 'Confirm Password'

        # Simplify password help text
        self.fields['password1'].help_text = 'Password must be at least 6 characters long and contain at least one number.'

        # Remove default validators
        self.fields['password1'].validators = []
        self.fields['password2'].validators = []

        # Update field labels in error messages
        self.fields['password2'].error_messages = {
            'required': 'Confirm Password is required.',
            'password_mismatch': 'Confirm Password does not match the Main Password.'
        }

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 6:
            raise ValidationError('Password must be at least 6 characters long.')
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one number.')
        return password

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

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                'Confirm Password does not match the Main Password.',
                code='password_mismatch'
            )
        return password2

    def clean(self):
        cleaned_data = super().clean()
        if 'password2' in self._errors:
            self._errors['password2'] = self.error_class([
                error.replace('password2', 'Confirm Password')
                for error in self._errors['password2']
            ])
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        # Split full name into first and last name
        full_name = self.cleaned_data['full_name'].split(' ', 1)
        user.first_name = full_name[0]
        user.last_name = full_name[1] if len(full_name) > 1 else ''

        if commit:
            user.save()
            # Create or update the StudentProfile
            StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    'full_name': self.cleaned_data['full_name'],
                    'phone': self.cleaned_data['phone']
                }
            )
        return user