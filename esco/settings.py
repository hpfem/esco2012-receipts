from os import path

DEBUG          = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Mateusz Paprocki', 'mattpap@gmail.com'),
)

MANAGERS = ADMINS

SITE_ID = 1

DATABASE_ENGINE   = 'mysql'
DATABASE_NAME     = 'esco'
DATABASE_USER     = 'esco'
DATABASE_PASSWORD = 'pass'
DATABASE_HOST     = 'localhost'
DATABASE_PORT     = '3306'

TIME_ZONE     = 'Europe/Warsaw'
LANGUAGE_CODE = 'en-us'
USE_I18N      = True

SECRET_KEY = 'hc!ww7a39saud9l1cigyda6e1!8!0!gs-!h-xd!a-y$)bsxmnl'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'esco.urls'

TEMPLATE_DIRS = (
    path.join(path.dirname(__file__), 'templates'),
)

MEDIA_ROOT = path.join(path.dirname(__file__), 'media')
MEDIA_URL  = '/'

ADMIN_MEDIA_PREFIX = MEDIA_ROOT

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'esco.site',
)

