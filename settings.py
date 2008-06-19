# Django settings for cargo project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DEFAULT_CHARSET = 'UTF-8'

ADMINS = (
    ('Ruslan Popov', 'radz@yandex.ru'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'      # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'cargo'        # Or path to database file if using sqlite3.
DATABASE_USER = 'cargo'        # Not used with sqlite3.
DATABASE_PASSWORD = 'XmeY4qu$&Calo2Oj' # Not used with sqlite3.
DATABASE_HOST = ''    # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''         # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/rad/django/cargo/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://cargo/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://cargo/adminmedia/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+&oxu(m-yg6#0am-pdcxb%^#ok(*w&w6gtrh8grdc3m3$=s(#j'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#    'cargo.djangobook.ziploader.load_template_source',
#    'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'cargo.urls'

DJANGOBOOK_PAGE_DIR = '/home/rad/django/djangobook-html'
DJANGOBOOK_PAGE_ZIP = '/home/rad/django/cargo/templates/djangobook.html.zip'

TEMPLATE_DIRS = (
    '/home/rad/django/cargo/templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.comments',
    'cargo',
    'cargo.djangobook',
    'cargo.shop',
)
