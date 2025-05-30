"""
Django settings for sportsanalytics project.

Generated by 'django-admin startproject' using Django 4.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

# Environment toggle: 'prod' for Render, 'local' for debugging
ENV = os.getenv('ENV', 'local')  # Defaults to 'local' if not set

actual_domain='thesmartlines.com'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
STRIPE_TEST_PUBLIC_KEY = os.getenv('STRIPE_TEST_PUBLIC_KEY')
STRIPE_TEST_SECRET_KEY = os.getenv('STRIPE_TEST_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')


AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
AWS_STORAGE_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY'] 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['api.thesmartlines.com', 'sports-bloomberg.onrender.com', 'localhost'] if ENV == 'prod' else ['10.0.0.29', 'localhost', '127.0.0.1', "192.168.2.46", 'www.thesmartlines.com', 'thesmartlines.com']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sports',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'django_extensions',
    "django_celery_beat",
    'whitenoise.runserver_nostatic'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# Allow your Next.js origin
CORS_ALLOWED_ORIGINS = ['https://thesmartlines.com', 'http://localhost:3000', "https://localhost:3000"] if ENV == 'prod' else ["https://localhost:3000", "http://localhost:3000"]

# Allow specific methods and headers
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # 'sports.middleware.SubscriptionCheckMiddleware',
]
CORS_ALLOWED_HEADERS = [
    'content-type',
    'Authorization',  # Make sure Authorization is allowed
]

ROOT_URLCONF = 'sportsanalytics.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'sports/templates/registration'],  # Add your specific templates folder
        'APP_DIRS': True,  # This ensures Django looks in app's templates directory
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

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


WSGI_APPLICATION = 'sportsanalytics.wsgi.application'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Parse DATABASE_URL and add SSL root cert
DATABASE_CONFIG = dj_database_url.config(
    default=os.environ['DATABASE_URL'],
    engine='django_cockroachdb',
    conn_max_age=600
)

# Add sslrootcert to OPTIONS
DATABASE_CONFIG['OPTIONS'] = DATABASE_CONFIG.get('OPTIONS', {})
DATABASE_CONFIG['OPTIONS']['sslmode'] = 'verify-full'
DATABASE_CONFIG['OPTIONS']['sslrootcert'] = os.path.join(BASE_DIR, 'certs', 'root.crt')

DATABASES = {
    'default': DATABASE_CONFIG
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

if ENV == 'prod':
    CELERY_BROKER_URL = os.getenv('REDIS_URL')
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv('REDIS_URL'),
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://localhost:6379/1",
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logsport.log",  # Logs will be saved here
            "formatter": "verbose",
        },
    },
    "loggers": {
        "logsport": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}



# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Allow all origins (development purposes)
CORS_ALLOW_ALL_ORIGINS = True

#registration
LOGIN_REDIRECT_URL = '/'  # Redirect to home page after successful login
LOGOUT_REDIRECT_URL = '/'  # Redirect to home page after logout

CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:3000', "http://192.168.2.46:3000"]

CORS_ALLOW_CREDENTIALS = True



CSRF_COOKIE_SECURE = True   # Ensures CSRF cookie is only sent over HTTPS
SESSION_COOKIE_SECURE = True  # Ensures session cookie is only sent over HTTPS
ACCESS_TOKEN_COOKIE_SECURE = True  # Custom setting if using token-based auth
REFRESH_TOKEN_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "None"

# email auth
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'



DOMAIN = "api.thesmartlines.com" if ENV == 'prod' else "127.0.0.1:8000/"  # Change this to your actual domain
SITE_URL = "https://thesmartlines.com" if ENV == 'prod' else "http://localhost:3000"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = True  # Redirect all HTTP requests to HTTPS
SECURE_HSTS_SECONDS = 31536000  # Enforce HTTPS for a year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True



CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
