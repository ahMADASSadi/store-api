from tempfile import gettempdir
from datetime import timedelta
from socket import gethostname
from pathlib import Path
import environ
import os


from django.utils.translation import gettext_lazy as _


BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(BASE_DIR/".env")
env = environ.Env()

SECRET_KEY = env.get_value("STORE_SECRET_KEY")

HOST_NAME = gethostname()

DEBUG = env.bool("STORE_DEBUG", default=True)

ALLOWED_HOSTS = ["localhost", "127.0.0.1"] if DEBUG else env.list(
    "STORE_ALLOWED_HOSTS", default=[])

INTERNAL_IPS = ["127.0.0.1"] if DEBUG else None

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

PROJECT_APPS = [
    "core",
    "store",
]

THIRD_PARTY_APPS = [
    "rest_framework_simplejwt",
    "drf_spectacular_sidecar",
    "django_celery_beat",
    "drf_spectacular",
    "graphene_django",
    "django_filters",
    "rest_framework",
]

THIRD_PARTY_APPS.append("debug_toolbar",) if DEBUG else None

INSTALLED_APPS += PROJECT_APPS + THIRD_PARTY_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MIDDLEWARE.append(
    'debug_toolbar.middleware.DebugToolbarMiddleware',) if DEBUG else None

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
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


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.get_value("STORE_DB_NAME"),
        'USER': env.get_value("STORE_DB_USERNAME"),
        'PASSWORD': env.get_value("STORE_DB_PASSWORD"),
        'HOST': env.get_value("STORE_DB_HOST"),
        'PORT': env.get_value("STORE_DB_PORT"),
    }
}


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

AUTH_USER_MODEL = "core.User"

# LANGUAGE_CODE = 'fa'

LANGUAGES = [
    ('en-us', _('English')),
    ('fa', _('Persian')),
    ('fr', _('French')),
]

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATH = [
    BASE_DIR/'locale',
]

STATIC_URL = 'static/'
STATIC_ROOT = 'static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = 'media/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(weeks=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'TITLE': 'Store API',
    'DESCRIPTION': 'General API documentation for E-Commerce',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}


CELERY_RESULT_BACKEND = f'redis://{env("STORE_CELERY_REDIS_HOST")}:{env("STORE_CELERY_REDIS_PORT")}/{env("STORE_REDIS_ASYNC_DB")}'
CELERY_BROKER_URL = f"redis://{env("STORE_CELERY_REDIS_HOST")}:{env("STORE_CELERY_REDIS_PORT")}/{env("STORE_REDIS_ASYNC_DB")}"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_TASK_ACKS_LATE = True


LOG_DIR = Path(gettempdir())/"store_logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {module} {process:d} {thread:d} - {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "json": {  # Structured JSON logging (useful for external logging systems)
            "format": "{{\"timestamp\": \"{asctime}\", \"level\": \"{levelname}\", \"message\": \"{message}\"}}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django.log",
            "formatter": "verbose",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 3,
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "errors.log",
            "formatter": "verbose",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 3,
        },
        "json_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "log.json",
            "formatter": "json",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["error_file", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "config": {
            "handlers": ["console", "file", "json_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

LOG_APPS = PROJECT_APPS

for app in LOG_APPS:
    LOGGING["handlers"][f"{app}_logs_file"] = {
        "level": "INFO",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": LOG_DIR / f"{app}_logs.log",
        "formatter": "verbose",
        "maxBytes": 5 * 1024 * 1024,  # 5 MB
        "backupCount": 3,
    }

    LOGGING["handlers"][f"{app}_errors_file"] = {
        "level": "ERROR",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": LOG_DIR / f"{app}_errors.log",
        "formatter": "verbose",
        "maxBytes": 5 * 1024 * 1024,  # 5 MB
        "backupCount": 3,
    }

    LOGGING["loggers"][app] = {
        "handlers": [f"{app}_logs_file", f"{app}_errors_file"],
        "level": "INFO",
        "propagate": False,
    }

LOGGING["handlers"]["rotating_file"] = {
    "level": "INFO",
    "class": "logging.handlers.RotatingFileHandler",
    "filename":  LOG_DIR/"rotating.log",
    "maxBytes": 1024 * 1024 * 5,
    "backupCount": 5,
    "formatter": "verbose",
}
