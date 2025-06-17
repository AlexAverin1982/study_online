import os
from pathlib import Path

from dotenv import load_dotenv

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'users.CustomUser'
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

CACHE_ENABLED = False
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
name = os.getenv("NAME")
user = os.getenv("USER")
dbuserpass = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")
engine = os.getenv("ENGINE")

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": name,
        "USER": user,
        "PASSWORD": dbuserpass,
        "HOST": host,
        "PORT": port,
    }
}

DEBUG = True

# e-mail settings
DEFAULT_FROM_EMAIL = os.getenv('SERVER_MAIL_USER')
EMAIL_HOST = os.getenv('SERVER_MAIL_HOST')
EMAIL_PORT = os.getenv('SERVER_MAIL_PORT')
EMAIL_HOST_USER = os.getenv('SERVER_MAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('SERVER_MAIL_PASSWORD')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
ADMIN_MAIL = os.getenv('ADMIN_MAIL')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    'django.contrib.sites',
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    "groupadmin_users",
    "materials",
    "users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_THOUSAND_SEPARATOR = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

SITE_ID = 1
STATIC_URL = "static/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
