"""
Django settings for designMatch project.

Generated by 'django-admin startproject' using Django 1.9.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from datetime import timedelta

# from mongoengine import connect

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# AWS S3 Credentials
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = False
AWS_S3_HOST = os.environ.get('AWS_S3_HOST')

CLOUDFRONT_DOMAIN = os.environ.get('AWS_CLOUDFRONT_DOMAIN')

STATICFILES_STORAGE = os.environ.get('STATICFILES_STORAGE')
STATIC_S3_PATH = 'static/'
STATIC_URL = '//%s/%s' % (CLOUDFRONT_DOMAIN, STATIC_S3_PATH)

# Tell the staticfiles app to use S3Boto storage when writing the collected static files (when you run `collectstatic`).
DEFAULT_FILE_STORAGE = os.environ.get('DEFAULT_FILE_STORAGE')

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'designMatchApp',
    'mongoAuthApp',
    'bootstrap3',
    'batchApp',
    'storages',
    's3_folder_storage',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'designMatch.urls'

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

WSGI_APPLICATION = 'designMatch.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

# DATABASES = {
#    'default': {
#        'ENGINE': os.environ.get('RDS_PG_ENGINE'),
#        'NAME': os.environ.get('RDS_PG_DBNAME'),
#        'USER': os.environ.get('RDS_PG_USERNAME'),
#        'PASSWORD': os.environ.get('RDS_PG_PASSWORD'),
#        'HOST': os.environ.get('RDS_PG_HOST'),
#        'PORT': os.environ.get('RDS_PG_PORT'),
#    }
# }


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

# CELERY SETTINGS
BROKER_URL = os.environ.get('SQS_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYBEAT_SCHEDULE = {'process-every-60-seconds':
    {
        'task': 'batchApp.tasks.procesar',
        'schedule': timedelta(seconds=60),
        'args': ()
    },
    'restore-every-30-seconds':
    {
        'task': 'batchApp.tasks.restaurar_disenios',
        'schedule': timedelta(seconds=30),
        'args': ()
    },
}

# SQS Configurations
BROKER_TRANSPORT = 'sqs'
BROKER_TRANSPORT_OPTIONS = {
    'region': os.environ.get('AWS_REGION'),
}
BROKER_USER = os.environ.get('AWS_ACCESS_KEY_ID')
BROKER_PASSWORD = os.environ.get('AWS_SECRET_ACCESS_KEY')
CELERY_DEFAULT_QUEUE = os.environ.get('SQS_QUEUE_NAME')
CELERY_QUEUES = {
    CELERY_DEFAULT_QUEUE: {
        'exchange': CELERY_DEFAULT_QUEUE,
        'binding_key': CELERY_DEFAULT_QUEUE,
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

# SES Configurations
EMAIL_BACKEND = 'django_ses.SESBackend'

# ElastiCache Configurations
# CACHES = {
#    'default': {
#        'BACKEND': os.environ.get('AWS_ELASTICACHE_BACKEND'),
#        'LOCATION': os.environ.get('AWS_ELASTICACHE_LOCATION'),
#    }
# }
