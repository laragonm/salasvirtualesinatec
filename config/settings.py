"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
from decouple import config, Csv
from dj_database_url import parse as db_url
import django_python3_ldap.utils

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool, default=True)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='*')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_python3_ldap',
    'solo',
    'minio_storage',
]

INSTALLED_APPS += [
    'apps.core',
    'apps.usuarios',
    'apps.catalogos',
    'apps.solicitudes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': config('DATABASE_URL', cast=db_url, default='sqlite:///db.sqlite3'),
    'inatec': config('DATABASE_URL_INATEC', cast=db_url),
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Managua'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email

EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=25)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=False)

# Login

LOGIN_URL = 'usuarios:login'

# LDAP

USE_LDAP = config('USE_LDAP', cast=bool, default=False)

if USE_LDAP:
    LDAP_AUTH_URL = config('LDAP_AUTH_URL', default='')
    LDAP_AUTH_USE_TLS = False
    LDAP_AUTH_SEARCH_BASE = "DC=inatec,DC=edu,DC=ni"
    LDAP_AUTH_OBJECT_CLASS = "organizationalPerson"

    LDAP_AUTH_USER_FIELDS = {
        "username": "sAMAccountName",
        "first_name": "givenName",
        "last_name": "sn",
        "email": "userPrincipalName",
    }

    AUTH_LDAP_USER_QUERY_FIELD = 'email'
    LDAP_AUTH_USER_LOOKUP_FIELDS = ("username",)
    LDAP_AUTH_CLEAN_USER_DATA = "django_python3_ldap.utils.clean_user_data"
    LDAP_AUTH_SYNC_USER_RELATIONS = "django_python3_ldap.utils.sync_user_relations"
    LDAP_AUTH_FORMAT_SEARCH_FILTERS = "django_python3_ldap.utils.format_search_filters"

    LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_active_directory"
    LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN = "inatec"

    LDAP_AUTH_CONNECTION_USERNAME = config('LDAP_AUTH_CONNECTION_USERNAME', default='')
    LDAP_AUTH_CONNECTION_PASSWORD = config('LDAP_AUTH_CONNECTION_PASSWORD', default='')

    AUTHENTICATION_BACKENDS = (
        'django_python3_ldap.auth.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "django_python3_ldap": {
                "handlers": ["console"],
                "level": "INFO",
            },
        },
    }

# Whitenoise

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MinIO Storage

DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
MINIO_STORAGE_ENDPOINT = config('MINIO_STORAGE_ENDPOINT', default='')
MINIO_STORAGE_ACCESS_KEY = config('MINIO_STORAGE_ACCESS_KEY', default='')
MINIO_STORAGE_SECRET_KEY = config('MINIO_STORAGE_SECRET_KEY', default='')
MINIO_STORAGE_USE_HTTPS = config('MINIO_STORAGE_USE_HTTPS', cast=bool, default=False)
MINIO_STORAGE_MEDIA_BUCKET_NAME = config('MINIO_STORAGE_MEDIA_BUCKET_NAME', default='')
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = config('MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET', cast=bool, default=True)

# Session Timeout

SESSION_EXPIRE_SECONDS = 3600
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD = 60
SESSION_TIMEOUT_REDIRECT = '/'

# Zoom API

ZOOM_API_KEY = config('ZOOM_API_KEY', default='')
ZOOM_API_SECRET = config('ZOOM_API_SECRET', default='')
ZOOM_PAGE_SIZE = config('ZOOM_PAGE_SIZE', cast=int, default=300)
ZOOM_TIMEOUT = config('ZOOM_TIMEOUT', cast=int, default=300)

# WebSite URL

WEBSITE_URL = config('WEBSITE_URL', default='')

# Locale Setting

LC_ES = config('LC_ES')
LC_EN = config('LC_EN')