import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


AUTH_USER_MODEL = "accounts.User"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
GOOGLE_CALENDAR_REDIRECT_URI = os.getenv(
    "GOOGLE_CALENDAR_REDIRECT_URI",
    "http://localhost:5173/calendar/google-callback",
)

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY", "django-insecure-change-me-please-override-this-in-env"
)
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = [
    host for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if host
]

# Dev profiling: django-debug-toolbar (/__debug__/ + admin) and django-silk (/silk/)
PROFILING_ENABLED = env_bool("PROFILING_ENABLED", DEBUG)
INTERNAL_IPS = [ip for ip in os.getenv("INTERNAL_IPS", "127.0.0.1").split(",") if ip]

LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "DEBUG" if DEBUG else "INFO").upper()
DJANGO_DB_LOG_LEVEL = os.getenv("DJANGO_DB_LOG_LEVEL", "INFO")

PROJECT_LOGGERS = [
    "accounts",
    "teams",
    "evaluation",
    "tournaments",
    "notifications",
    "stats",
    "news",
    "backend",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "rename_fields": {
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger",
            },
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        **{
            name: {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False}
            for name in PROJECT_LOGGERS
        },
        "django.db.backends": {"level": DJANGO_DB_LOG_LEVEL},
    },
}

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "teams",
    "evaluation",
    "tournaments",
    "corsheaders",
    "rest_framework_simplejwt",
    "notifications",
    "stats",
    "news",
    "channels",
    "devtools",
]

if PROFILING_ENABLED:
    INSTALLED_APPS += ["debug_toolbar", "silk"]

MIDDLEWARE = [
    "ninja.compatibility.files.fix_request_files_middleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if PROFILING_ENABLED:
    # Silk records everything first; the debug toolbar must sit *after*
    # GZipMiddleware (django-debug-toolbar check W003).
    _gzip = "django.middleware.gzip.GZipMiddleware"
    _after_gzip = MIDDLEWARE.index(_gzip) + 1
    MIDDLEWARE = [
        "silk.middleware.SilkyMiddleware",
        *MIDDLEWARE[:_after_gzip],
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *MIDDLEWARE[_after_gzip:],
    ]

CORS_ALLOWED_ORIGINS = [
    origin
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin
]
CORS_ALLOW_CREDENTIALS = True

JWT_ACCESS_COOKIE_NAME = 'access_token'
JWT_REFRESH_COOKIE_NAME = 'refresh_token'
JWT_CSRF_COOKIE_NAME = 'csrf_token'
JWT_COOKIE_SECURE = env_bool('JWT_COOKIE_SECURE', not DEBUG)
JWT_COOKIE_SAMESITE = os.getenv('JWT_COOKIE_SAMESITE', 'Lax')

FRONTEND_URL = os.getenv("FRONTEND_URL", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

ROOT_URLCONF = "backend.urls"

APPEND_SLASH = True

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

WSGI_APPLICATION = "backend.wsgi.application"
ASGI_APPLICATION = "backend.asgi.application"

# ---------------------------------------------------------------------------
# Redis: cache + channel layer (falls back to in-process defaults locally)
# ---------------------------------------------------------------------------

REDIS_URL = os.getenv("REDIS_URL", "")

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                # Don't take the whole site down if Redis is briefly unreachable.
                "IGNORE_EXCEPTIONS": True,
            },
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        }
    }
else:
    # Local dev without Redis: per-process fallbacks (WebSocket fan-out
    # only works within a single process in this mode).
    CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
    }

# ---------------------------------------------------------------------------
# Celery (background tasks: emails, Google Calendar sync, notification drain)
# ---------------------------------------------------------------------------

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL or "redis://localhost:6379/1")
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# Run tasks inline when no broker is configured (local dev without Redis).
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", not REDIS_URL)
CELERY_BEAT_SCHEDULE = {
    # Retries NotificationDeliveryTask rows whose next_attempt_at has passed,
    # complementing the in-process dispatcher triggered on_commit.
    "drain-notification-deliveries": {
        "task": "notifications.drain_pending_deliveries",
        "schedule": 60.0,
    },
}

# ---------------------------------------------------------------------------
# Dev profiling: django-debug-toolbar (/__debug__/) + django-silk (/silk/)
# ---------------------------------------------------------------------------

if PROFILING_ENABLED:
    # Record every request with SQL queries, timelines etc. View at /silk/.
    SILKY_AUTHENTICATION = True  # require a logged-in session
    SILKY_AUTHORISATION = True   # require staff
    SILKY_MAX_RECORDED_REQUESTS = 1000
    SILKY_INTERCEPT_PERCENT = int(os.getenv("SILKY_INTERCEPT_PERCENT", "100"))
    SILKY_IGNORE_PATHS = [r"^/static/", r"^/media/", r"^/__debug__/"]

DB_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.getenv("DB_NAME", "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": os.getenv("DB_NAME", "itturik"),
            "USER": os.getenv("DB_USER", "itturik"),
            "PASSWORD": os.getenv("DB_PASSWORD", "itturik"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }

    # Built-in psycopg3 connection pool (Django 5.1+; requires psycopg[pool]).
    # Only used by the PostgreSQL backend; ignored for SQLite.
    #
    # Disable with DB_POOL_ENABLED=false when an external pooler (PgBouncer in
    # transaction mode) sits in front: pools must not nest, otherwise every
    # worker holds its full pool and the pooler cannot multiplex connections.
    if env_bool("DB_POOL_ENABLED", True):
        DATABASES["default"]["pool"] = {
            "min_size": int(os.getenv("DB_POOL_MIN_SIZE", "2")),
            "max_size": int(os.getenv("DB_POOL_MAX_SIZE", "10")),
            "timeout": float(os.getenv("DB_POOL_TIMEOUT", "30")),
            "max_lifetime": int(os.getenv("DB_POOL_MAX_LIFETIME", "3600")),
            "max_idle": int(os.getenv("DB_POOL_MAX_IDLE", "600")),
        }

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
WHITENOISE_MANIFEST_STRICT = False

# Product forms may include several images in one multipart request.
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
