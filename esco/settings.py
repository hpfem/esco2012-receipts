from os import path

#
# Configuration file must contain:
#
# DATABASE_ENGINE
# DATABASE_NAME
# DATABASE_USER
# DATABASE_PASSWORD
# DATABASE_HOST
# DATABASE_PORT
# DEBUG
#
# See Django documentation for possible values.
#

conf = open('/etc/esco-2010.conf', 'r')

for line in conf:
    exec line

conf.close()

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Mateusz Paprocki', 'mattpap@gmail.com'),
)

MANAGERS = ADMINS

SITE_ID = 1

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
    'esco.contrib.nocache.NoCacheIfAuthenticatedMiddleware',
)

ROOT_URLCONF = 'esco.urls'

TEMPLATE_DIRS = (
    path.join(path.dirname(__file__), 'templates'),
)

MEDIA_ROOT = path.join(path.dirname(__file__), 'media')
MEDIA_URL  = '/events/esco-2010/media/'

ADMIN_MEDIA_PREFIX = '/events/esco-2010/media/admin/'

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'esco.site',
)

DEFAULT_CONTENT_TYPE = 'text/html'

MIN_PASSWORD_LEN = 6
CHECK_STRENGTH = True

CAPTCHA = {
    'fgcolor': '#254b6f',
    'imagesize': (200, 50),
}

LOGIN_URL = '/events/esco-2010/account/login/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

AUTH_PROFILE_MODULE = 'site.UserProfile'

ABSTRACTS_PATH = '/var/db/esco-2010/abstracts/'

