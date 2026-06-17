from pathlib import Path
import os
import cloudinary

# ─── Load .env in development ─────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
except ImportError:
    pass  # python-dotenv not installed; rely on real environment variables

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-mvnp-research-repo-dev-key-2024')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Cloudinary — must come before your app
    'cloudinary_storage',
    'cloudinary',
    'mvnp_repo',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Allow the PDF proxy view to be embedded in an iframe on the same origin.
X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'mvnp_repo.context_processors.applicant_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

# ─── Email ────────────────────────────────────────────────────────────────────
# Development: prints emails to the console.
# Switch to the SMTP block below when deploying to production.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@mvnp.gov.ph'

# MVNP staff notification address (receives alerts on every new application).
MVNP_NOTIFICATION_EMAIL = 'mvnp@denr.gov.ph'

# ─── Production SMTP (uncomment and fill in when going live) ──────────────────
# EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST         = 'smtp.your-mail-provider.com'
# EMAIL_PORT         = 587
# EMAIL_USE_TLS      = True
# EMAIL_HOST_USER    = 'your-sending-address@domain.com'
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# ─────────────────────────────────────────────────────────────────────────────

# ─── Cloudinary ───────────────────────────────────────────────────────────────
# Credentials are read from environment variables (set them in .env locally,
# or in your hosting dashboard in production — never hardcode them here).
import cloudinary

cloudinary.config(
    cloud_name = 'diggprybb',
    api_key    = '241161852468148',
    api_secret = 'EmhP6Y6X6jJPmfYNLiim-dF7cEg',
    secure     = True,
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.RawMediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME' : 'diggprybb',
    'API_KEY'    : '241161852468148',
    'API_SECRET' : 'EmhP6Y6X6jJPmfYNLiim-dF7cEg',
    'RESOURCE_TYPE': 'auto',
    'UNSIGNED_UPLOADS': True,  # ✅ Allow public/unsigned uploads
}
# ─────────────────────────────────────────────────────────────────────────────

# Keep local MEDIA settings as fallback when Cloudinary is not configured.
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'