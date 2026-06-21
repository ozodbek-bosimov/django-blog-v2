"""
Django settings for blogApp project.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load exactly one env file (default: .env). Use DJANGO_ENV_FILE=.env.deploy for production.
_env_file_name = os.getenv("DJANGO_ENV_FILE", ".env")
load_dotenv(BASE_DIR / _env_file_name)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# For local development you can keep this default, but in production
# always override it via the DJANGO_SECRET_KEY environment variable.
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-1xw9u!m7f^z0&g2p_@k3s8r#q5b%v4h+lnc7d1e",
)


def _get_bool_env(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _get_bool_env("DJANGO_DEBUG", False)
STATIC_ASSET_VERSION = os.getenv("APP_STATIC_ASSET_VERSION", "20260621_06")

_allowed_hosts = os.getenv("DJANGO_ALLOWED_HOSTS")
if not (_allowed_hosts and _allowed_hosts.strip()):
    # Safe defaults:
    # - In dev (DEBUG=True): allow everything for convenience.
    # - In non-debug (DEBUG=False): allow local/test hosts so manage.py commands,
    #   smoke scripts, and simple local runs don't fail with DisallowedHost.
    #   Production should always provide DJANGO_ALLOWED_HOSTS explicitly.
    _allowed_hosts = "*" if DEBUG else "localhost,127.0.0.1,0.0.0.0,[::1],testserver"

ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts.split(",") if host.strip()]

_csrf_trusted_origins = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in _csrf_trusted_origins.split(",") if origin.strip()
]


# Application definition

INSTALLED_APPS = [
    "django_ckeditor_5",
    "home.apps.HomeConfig",
    "django.contrib.sitemaps",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "blogApp.middleware.DevStaticNoCacheMiddleware",
    "blogApp.middleware.IpRateLimitMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "blogApp.middleware.AdminSessionTimeoutMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "blogApp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "home.context_processors.used_tags",
                "home.context_processors.static_asset_version",
                "home.context_processors.about_me",
            ],
        },
    },
]

WSGI_APPLICATION = "blogApp.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# To use PostgreSQL, set these environment variables and update DATABASES accordingly:
# DJANGO_DB_ENGINE, DJANGO_DB_NAME, DJANGO_DB_USER, DJANGO_DB_PASSWORD, DJANGO_DB_HOST, DJANGO_DB_PORT

# Cache configuration
# Keep cache setup simple and provider-agnostic.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

# TIME_ZONE = 'UTC'
TIME_ZONE = "Asia/Tashkent"

USE_I18N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
SHARED_URL = "/shared/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
SHARED_ROOT = os.path.join(BASE_DIR, "shared")

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

if not DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }


# EMAIL CONFIGURATION (disabled - contact form removed)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security/cookie settings for production. Override via environment variables.
SESSION_COOKIE_SECURE = _get_bool_env("DJANGO_SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = _get_bool_env("DJANGO_CSRF_COOKIE_SECURE", not DEBUG)
SECURE_SSL_REDIRECT = _get_bool_env("DJANGO_SECURE_SSL_REDIRECT", not DEBUG)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Global request rate limiting.
GLOBAL_RATE_LIMIT_ENABLED = _get_bool_env("GLOBAL_RATE_LIMIT_ENABLED", not DEBUG)
GLOBAL_RATE_LIMIT_REQUESTS = int(os.getenv("GLOBAL_RATE_LIMIT_REQUESTS", "120"))
GLOBAL_RATE_LIMIT_WINDOW_SECONDS = int(
    os.getenv("GLOBAL_RATE_LIMIT_WINDOW_SECONDS", "60")
)
GLOBAL_RATE_LIMIT_BLOCK_SECONDS = int(
    os.getenv("GLOBAL_RATE_LIMIT_BLOCK_SECONDS", "120")
)
_global_rl_exempt = os.getenv(
    "GLOBAL_RATE_LIMIT_EXEMPT_PATH_PREFIXES",
    "/_owner/,/static/,/media/,/shared/",
)
GLOBAL_RATE_LIMIT_EXEMPT_PATH_PREFIXES = [
    p.strip() for p in _global_rl_exempt.split(",") if p.strip()
]

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
# HSTS: 0 in dev (DEBUG=True), 1 year in production. Override via env.
SECURE_HSTS_SECONDS = (
    0 if DEBUG else int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# Admin session timeout (seconds). Defaults to 30 minutes.
ADMIN_SESSION_TIMEOUT = int(os.getenv("ADMIN_SESSION_TIMEOUT", "1800"))
SESSION_COOKIE_AGE = 86400  # 1 day expiration
SESSION_SAVE_EVERY_REQUEST = False  # Save only when changed to prevent DB bloat

# Admin history (django_admin_log) retention.
# Keep only the most recent N days to prevent unbounded growth.
ADMIN_LOG_RETENTION_ENABLED = _get_bool_env("ADMIN_LOG_RETENTION_ENABLED", True)
ADMIN_LOG_RETENTION_DAYS = int(os.getenv("ADMIN_LOG_RETENTION_DAYS", "90"))

# Upload limits – must be smaller than Nginx client_max_body_size (20m).
# Images are compressed to WebP during model.save(), but the *original*
# must first pass through Django's request parser at full size.
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# CKEditor 5 configuration
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "highlight",
            "-",
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "subscript",
            "superscript",
            "code",
            "removeFormat",
            "-",
            "link",
            "bulletedList",
            "numberedList",
            "todoList",
            "outdent",
            "indent",
            "alignment",
            "-",
            "imageUpload",
            "insertTable",
            "mediaEmbed",
            "blockQuote",
            "codeBlock",
            "horizontalLine",
            "specialCharacters",
            "-",
            "sourceEditing",
            "|",
            "undo",
            "redo",
        ],
        "list": {
            "properties": {
                "styles": True,
                "startIndex": True,
                "reversed": True,
            }
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
                {
                    "model": "heading4",
                    "view": "h4",
                    "title": "Heading 4",
                    "class": "ck-heading_heading4",
                },
            ]
        },
        "height": "400px",
        "width": "100%",
        "placeholder": "Write your content here...",
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "imageStyle:alignLeft",
                "imageStyle:alignCenter",
                "imageStyle:alignRight",
                "toggleImageCaption",
                "linkImage",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ]
        },
        "htmlSupport": {
            "allow": [
                {
                    "name": "/.*/",
                    "attributes": True,
                    "classes": True,
                    "styles": True,
                }
            ]
        },
        "mediaEmbed": {
            "previewsInData": True,
        },
        "link": {
            "addTargetToExternalLinks": True,
            "defaultProtocol": "https://",
        },
        "removePlugins": ["Markdown", "Style"],
    },
}

# Extra editor-only CSS loaded by django-ckeditor-5 widget (admin form).
CKEDITOR_5_CUSTOM_CSS = "css/ckeditor_admin_fix.css"

CKEDITOR_5_UPLOAD_FILE_TYPES = ["jpeg", "jpg", "png", "gif", "bmp", "webp", "svg"]
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = False

# Route CKEditor inline uploads to media/postimages/
CKEDITOR_5_FILE_STORAGE = "home.storage.CKEditor5Storage"

CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"

# Basic file logging to capture production errors.
LOG_DIR = os.path.join(BASE_DIR, "logs")
_file_logging_enabled = _get_bool_env("DJANGO_FILE_LOGGING", False)
if _file_logging_enabled:
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except PermissionError:
        _file_logging_enabled = False
_log_dir_writable = os.access(LOG_DIR, os.W_OK)
if _file_logging_enabled and _log_dir_writable:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_DIR, "django.log"),
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["file"],
                "level": "ERROR",
                "propagate": True,
            },
        },
    }
