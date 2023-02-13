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
import google.auth

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Attempt to load the Project ID into the environment, safely failing on error.
try:
    _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
except google.auth.exceptions.DefaultCredentialsError:
    pass


# Load environment
load_dotenv()

# Pull secrets from Secret Manager
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

def access_secret(project_id, secret_str):
    """
    Desc: Access secret in GCP Secrets Manager

    Parameters:
    project_id --- GCP project ID
    secret_str --- name of secret (Eg MY_SECRET_KEY)

    Returns:
    secret_val --- value of secret (including single quotes)
    """
    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME", project_id)
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

    # Extract value for secret (either before newline or at end of values)
    secret_val = re.search(f'(?<={secret_str}=).*(?=\\n|'')', payload)[0]

    return secret_val

SECRET_KEY = access_secret(project_id, 'SECRET_KEY')
WEATHER_API_KEY = access_secret(project_id, 'WEATHER_API_KEY')

# Set DEBUG=False for production
DEBUG = bool(int(os.environ.get('DEBUG', 0)))

# SECURITY WARNING: It's recommended that you use this when
# running in production. The URL will be known once you first deploy
# to Cloud Run. This code takes the URL and converts it to both these settings formats.

# Set allowed hosts to all for local development
if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", None):
    print("Running app locally using cloud sql auth proxy...")
    ALLOWED_HOSTS = ["*"]

# Use deployed url in production
#CLOUDRUN_SERVICE_URL = os.environ.get("CLOUDRUN_SERVICE_URL", default=None)
else:
    CLOUDRUN_SERVICE_URL = access_secret(project_id, 'CLOUDRUN_SERVICE_URL')
    print("cloudrun:", CLOUDRUN_SERVICE_URL)
    ALLOWED_HOSTS = [urlparse(CLOUDRUN_SERVICE_URL).netloc]
    CSRF_TRUSTED_ORIGINS = [CLOUDRUN_SERVICE_URL]
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'storages', # GCP static file storage
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

# Static files (CSS, JavaScript, Images)
# [START cloudrun_django_static_config]
# Define static storage via django-storages[google]
if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", None):
    #print("Running app locally...")
    STATIC_URL = '/static/'
    #STATICFILES_DIRS = [BASE_DIR / 'static']
    STATIC_ROOT = BASE_DIR / 'staticfiles' # use staticfiles to align with .gitignore
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

else:
    GS_BUCKET_NAME=access_secret(project_id, 'GS_BUCKET_NAME')
    STATIC_URL = '/static/'
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_QUERYSTRING_AUTH = False
    GS_DEFAULT_ACL = None

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'