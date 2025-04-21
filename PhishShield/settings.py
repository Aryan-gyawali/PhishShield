import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key-here'  # Replace with a real secret key

DEBUG = True

ALLOWED_HOSTS = ['*']


# Minimal installed apps (no admin or auth)
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'simulator',  # Your app
]

# Minimal middleware (no auth middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'phishshield.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'phishshield.wsgi.application'

# Completely disable database
DATABASES = {}

# Disable internationalization if not needed
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = False

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Cookie-based sessions (no database)
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_NAME = 'phishshield_session'

# Disable all auth-related settings
AUTHENTICATION_BACKENDS = []
PASSWORD_HASHERS = []