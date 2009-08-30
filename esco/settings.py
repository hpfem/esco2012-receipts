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

import re

def _add_to_header(response, key, value):
    if response.has_header(key):
        values = re.split(r'\s*,\s*', response[key])
        if not value in values:
            response[key] = ', '.join(values + [value])
    else:
        response[key] = value

def _nocache_if_auth(request, response):
    if request.user.is_authenticated():
        _add_to_header(response, 'Cache-Control', 'no-store')
        _add_to_header(response, 'Cache-Control', 'no-cache')
        _add_to_header(response, 'Pragma', 'no-cache')
    return response

class NoCacheIfAuthenticatedMiddleware(object):
    def process_response(self, request, response):
        try:
            return _nocache_if_auth(request, response)
        except:
            return response

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'esco.settings.NoCacheIfAuthenticatedMiddleware',
)

ROOT_URLCONF = 'esco.urls'

TEMPLATE_DIRS = (
    path.join(path.dirname(__file__), 'templates'),
)

MEDIA_ROOT = path.join(path.dirname(__file__), 'media')
MEDIA_URL  = '/esco/media/'

ADMIN_MEDIA_PREFIX = '/esco/media/admin/'

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'esco.site',
)

MIN_PASSWORD_LEN = 8
CHECK_STRENGTH = False

CAPTCHA = {
    'fgcolor': '#254b6f',
    'imagesize': (200, 50),
}

LOGIN_URL = '/esco/account/login/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

AUTH_PROFILE_MODULE = 'site.UserProfile'

