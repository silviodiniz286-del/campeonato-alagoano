from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================
# SEGURANÇA
# ==========================

SECRET_KEY = 'django-insecure-campeonato-alagoano-2026'

DEBUG = True

ALLOWED_HOSTS = ['*']


# ==========================
# APPS
# ==========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'campeonato',
]


# ==========================
# MIDDLEWARE
# ==========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ==========================
# URLS
# ==========================

ROOT_URLCONF = 'config.urls'


# ==========================
# TEMPLATES
# ==========================

TEMPLATES = [
    {
        'BACKEND':
        'django.template.backends.django.DjangoTemplates',

        'DIRS': [],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ==========================
# WSGI
# ==========================

WSGI_APPLICATION = 'config.wsgi.application'


# ==========================
# DATABASE
# ==========================

DATABASES = {
    'default': {
        'ENGINE':
        'django.db.backends.sqlite3',

        'NAME':
        BASE_DIR / 'db.sqlite3',
    }
}


# ==========================
# SENHAS
# ==========================

AUTH_PASSWORD_VALIDATORS = []


# ==========================
# IDIOMA
# ==========================

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Maceio'

USE_I18N = True

USE_TZ = True


# ==========================
# STATIC
# ==========================

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# ==========================
# MEDIA (logos dos times)
# ==========================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ==========================
# AUTO FIELD
# ==========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'