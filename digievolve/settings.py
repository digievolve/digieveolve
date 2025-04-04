"""
Django settings for digievolve project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_i$$c-5@f8swp^b7tn+x!!l8d*77r5rz8tn#!xznv=7yzni@6@'





# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'tailwind',
    'compressor',
    'django_browser_reload',
    'widget_tweaks',
    'django_paystack',
    'courses',
    'utils',
    'blog',
    'resources',
    
    # Local apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'services.apps.ServicesConfig',
]

# reCAPTCHA settings
RECAPTCHA_PUBLIC_KEY = 'your_public_key_here'
RECAPTCHA_PRIVATE_KEY = 'your_private_key_here'
# Use the following for local development/testing:
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
]


from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'bg-gray-100 text-gray-700',
    messages.INFO: 'bg-blue-100 text-blue-700',
    messages.SUCCESS: 'bg-green-100 text-green-700',
    messages.WARNING: 'bg-yellow-100 text-yellow-700',
    messages.ERROR: 'bg-red-100 text-red-700',
}


ROOT_URLCONF = 'digievolve.urls'

# Paystack settings
PAYSTACK_PUBLIC_KEY = 'pk_test_f75b89d4b0b77d11c41a01491f5b6060862ee616'
PAYSTACK_SECRET_KEY = 'sk_test_d495b7568946469c62d1cd564d5b24bcec017762'
PAYSTACK_SUCCESS_URL = 'courses:payment_success'
PAYSTACK_FAILED_URL = 'courses:payment_failed'


PAYSTACK_SETTINGS = {
    'PUBLIC_KEY': PAYSTACK_PUBLIC_KEY,
    'SECRET_KEY': PAYSTACK_SECRET_KEY,
    'CALLBACK_URL': PAYSTACK_SUCCESS_URL,
    'BUTTON_ID': 'paystack-button',  # Default button ID for Paystack
    'CURRENCY': 'NGN',  # Add this line to specify the currency
    'BUTTON_CLASS': 'btn btn-primary',
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Add this line
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'digievolve.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Static files settings
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

DEBUG = 'RENDER' not in os.environ

if DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'digievolvehub.com', 'www.digievolvehub.com', 'digieveolve-620934795638.us-central1.run.app']
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    ALLOWED_HOSTS = [
    '.ondigitalocean.app',  # Add your DigitalOcean app hostname
    '127.0.0.1',  # For local development
    'localhost',  # For local development
    'digieveolve.onrender.com', 'oyster-app-gevod.ondigitalocean.app', 'digievolvehub.com', 'www.digievolvehub.com', 'digieveolve-620934795638.us-central1.run.app'
]
    # Security settings for production
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    CSRF_TRUSTED_ORIGINS = ['https://digieveolve.onrender.com', 'https://digievolvehub.com', 'https://www.digievolvehub.com']
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files settings
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CLOUDFLARE_TURNSTILE_SECRET_KEY = '0x4AAAAAAA_PrYbgupT5euhBSvuwBQzu0h0'
CLOUDFLARE_TURNSTILE_SITE_KEY = '0x4AAAAAAA_PrbdWkaPF_0vd'

TEMPLATES[0]['OPTIONS']['context_processors'].append('accounts.context_processors.settings_context')