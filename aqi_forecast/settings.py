"""
Django settings for aqi_forecast project.
Generated by 'django-admin startproject' using Django 4.1.5.
For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
import io
import re
import environ
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse
from google.cloud import secretmanager

# Build paths inside the project like this: BASE_DIR / 'subdir'.
#BASE_DIR = Path(__file__).resolve().parent.parent

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment
load_dotenv()
'''
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!

# API key for air quality data
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

#DEBUG = True
DEBUG = bool(int(os.environ.get('DEBUG', 0)))


#ALLOWED_HOSTS = ['predict-aqi.onrender.com', 'localhost', '127.0.0.1']
ALLOWED_HOSTS = ['*']'''




# [START gaestd_py_django_secret_config]
#env = environ.Env(DEBUG=(bool, False))
#env_file = os.path.join(BASE_DIR, ".env")

#if os.path.isfile(env_file):
#    # Use a local secret file, if provided
#
#    env.read_env(env_file)
# [START_EXCLUDE]
#elif os.getenv("TRAMPOLINE_CI", None):
#    # Create local settings if running with CI, for unit testing
#
#    placeholder = (
#        f"SECRET_KEY=a\n"
#        f"DATABASE_URL=sqlite://{os.path.join(BASE_DIR, 'db.sqlite3')}"
#    )
#    env.read_env(io.StringIO(placeholder))
# [END_EXCLUDE]
'''elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    # Pull secrets from Secret Manager
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    client = secretmanager.SecretManagerServiceClient()
    ***REMOVED***
    ***REMOVED***
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

    env.read_env(io.StringIO(payload))'''
#else:
#    raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")
# Pull secrets from Secret Manager
#project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
***REMOVED***

#client = secretmanager.SecretManagerServiceClient()
***REMOVED***
***REMOVED***
#name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
#payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

def access_secret(project_id, secret_str):
    """
    Access secret in GCP Secrets Manager
    """
    client = secretmanager.SecretManagerServiceClient()
    ***REMOVED***
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

    # Extract value for secret (either before newline or at end of values)
    secret_val = re.search(f'(?<={secret_str}=).*(?=\\n|'')', payload)[0]

    return secret_val

SECRET_KEY = access_secret(project_id, 'SECRET_KEY')
WEATHER_API_KEY = access_secret(project_id, 'WEATHER_API_KEY')

# [END gaestd_py_django_secret_config]

#SECRET_KEY = env("SECRET_KEY")
#SECRET_KEY = payload.get("SECRET_KEY") #or payload.get("_SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
# Change this to "False" when you are ready for production
#DEBUG = env("DEBUG")

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = os.environ.get('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!

# API key for air quality data
#WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
#WEATHER_API_KEY = payload.get("WEATHER_API_KEY")

#DEBUG = True
DEBUG = bool(int(os.environ.get('DEBUG', 0)))


#ALLOWED_HOSTS = ['predict-aqi.onrender.com', 'localhost', '127.0.0.1']
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'backend.apps.BackendConfig',
    'frontend.apps.FrontendConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

ROOT_URLCONF = 'aqi_forecast.urls'

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

WSGI_APPLICATION = 'aqi_forecast.wsgi.application'

# Specify path for machine learning model
MODELS = os.path.join(BASE_DIR, 'ml/models')

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': BASE_DIR / 'db.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
    }
}

# Use django-environ to parse the connection string
#DATABASE_URL=access_secret(project_id, 'DATABASE_URL')
#DATABASES = {"default": env.db()}
#DATABASES = {"default": DATABASE_URL}

# If the flag as been set, configure to use proxy
#if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", None):
#    DATABASES["default"]["HOST"] = "127.0.0.1"
#    DATABASES["default"]["PORT"] = 5432


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

#STATIC_URL = '/static/'
#STATICFILES_DIRS = [BASE_DIR / 'static']
#STATIC_ROOT = BASE_DIR / 'staticfiles'
#STATIC_ROOT = '/static'

# GCP sample
#STATIC_ROOT = "static"
#STATIC_URL = "/static/"
#STATICFILES_DIRS = []

# Static files (CSS, JavaScript, Images)
# [START cloudrun_django_static_config]
# Define static storage via django-storages[google]
GS_BUCKET_NAME=access_secret(project_id, 'GS_BUCKET_NAME')
STATIC_URL = "/static/"
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_DEFAULT_ACL = "publicRead"

# MEDIA_URL = "/media/"
# MEDIAFILES_DIRS = [BASE_DIR / "media"]  # new
# MEDIA_ROOT = BASE_DIR / "mediafiles"  # new

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'