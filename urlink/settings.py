"""
Django settings for urlink project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import datetime
import json
import os
from socket import gethostname

import redis

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$@m!+cqav*c!i2&x8+ys)d)#mv^zdh_z=*=7r9*f@6vg@f8b1g'
GOOGLE_API_KEY = 'AIzaSyD9VzCBawbBZR6LNJdbFWVJF_HYdiGQc_Y'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'server',
    'corsheaders',

    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'channels',

    'drf_yasg',
    'debug_toolbar',
    'django_crontab',
]

AUTH_USER_MODEL = 'server.User'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'EXCEPTION_HANDLER': 'server.exceptions.server_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'error_text'
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'request_logging.middleware.LoggingMiddleware',
]

ROOT_URLCONF = 'urlink.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'urlink.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
if gethostname().startswith('urlink'):
    DEBUG = False
    secrets = json.load(open(os.path.join(os.path.join(BASE_DIR, 'urlink'), 'secrets.json'), 'rb'))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'urlink_database',  # DB명
            'USER': secrets['DATABASES_USER'],  # 데이터베이스 계정
            'PASSWORD': secrets['DATABASES_PASSWORD'],  # 계정 비밀번호
            'HOST': secrets['DATABASES_HOST'],  # 데이테베이스 주소(IP)
            'PORT': '3306',  # 데이터베이스 포트(보통은 3306)
            'OPTIONS': {
                'charset': 'utf8mb4'
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'server/v1/url/static')
]

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'JWT': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=30),
    'AUTH_HEADER_TYPES': ('JWT',),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            '()': 'logs.CustomFormatter',
            'format': '{sql}',
            'style': '{',
        }
    },
    'handlers': {
        'sql': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/db.backends.sql.log'),
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'simple',
        }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['sql'],
            'level': 'DEBUG',  # change debug level as appropiate
        },
        # 'django.request': {
        #     'handlers': ['request'],
        #     'propagate': False,
        #     'level': 'DEBUG',
        # },
    },
}

ASGI_APPLICATION = "urlink.routing.application"

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

if gethostname().startswith('johongje-'):
    CRONJOBS_LOG_PATH = '/Users/hongjae/develop/Team_Web_1_Backend/logs/cronjob.log'
else:
    CRONJOBS_LOG_PATH = '/home/ubuntu/projects/Team_Web_1_Backend/logs/cronjob.log'

CRONJOBS = [
    ('* * * * *', 'server.v1.alarm.scheduler.get_alarms',
     f'> {CRONJOBS_LOG_PATH} 2>&1'),
]
CRONTAB_LOCK_JOBS = True

REDIS_CONNECTION_POOL = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
REDIS = redis.Redis(connection_pool=REDIS_CONNECTION_POOL)
