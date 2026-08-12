"""
Base settings shared by all environments for the KIPS College Kasur
Campus Management System.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-change-me-in-.env')

DEBUG = env('DJANGO_DEBUG', default=False)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'tailwind',
    'theme',
    'rest_framework',
]

LOCAL_APPS = [
    'apps.common',
    'apps.accounts',
    'apps.academics',
    'apps.attendance',
    'apps.daybook',
    'apps.assessments',
    'apps.timetable',
    'apps.finance',
    'apps.reports',
    'apps.dashboard',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.common.middleware.RoleContextMiddleware',
    'apps.common.middleware.ForcePasswordChangeMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.common.context_processors.role_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database

DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
}


# Custom user model

AUTH_USER_MODEL = 'accounts.User'


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True


# Static & media files

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Auth redirects

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:redirect'
LOGOUT_REDIRECT_URL = 'accounts:login'


# django-tailwind

TAILWIND_APP_NAME = 'theme'
NPM_BIN_PATH = env('NPM_BIN_PATH', default='npm.cmd')


# Attendance

ATTENDANCE_SHORTAGE_THRESHOLD = env.int('ATTENDANCE_SHORTAGE_THRESHOLD', default=75)


# Django REST Framework
#
# Templates are being migrated to fetch their data from these APIs via JS
# instead of receiving it through the Django view's template context (see
# apps/common/api_permissions.py and apps/common/api_generic.py). Auth reuses
# the same session cookie the HTML site already logs in with - no separate
# API login exists yet. JSON-only rendering (no browsable API) keeps this
# consistent with the fact that these endpoints are gated by the same
# role-based rules as the HTML views, not meant as a public/explorable API.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.common.api_metadata.StandardPagination',
    'PAGE_SIZE': 50,  # matches apps/common/crud.py CrudListView.paginate_by
    'DEFAULT_METADATA_CLASS': 'apps.common.api_metadata.ChoiceMetadata',
}
