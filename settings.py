import os

# Django settings for tdsurface project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'tdsurface'             # Or path to database file if using sqlite3.
DATABASE_USER = 'tdsurface'             # Not used with sqlite3.
DATABASE_PASSWORD = 'scimitar1'         # Not used with sqlite3.
DATABASE_HOST = 'surfacesystem.dev.teledrill'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.getcwd(),'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/tdsurface/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*2sp)6+q2zf2j$xa1&9=*ddp#-1n+1#s@&gv*f%d6z%2a5g3qx'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'tdsurface.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'tdsurface.depth',
    'tdsurface.las',
    'tdsurface.manual_depth',
    'tdsurface.plot',
    'tdsurface.bha',
    'tdsurface.daq',
    'tdsurface.toollog',
)

STATIC_DOC_ROOT = os.path.join(os.getcwd(),'media')

#print "!",STATIC_DOC_ROOT

#COMPORT = '/dev/tty.BluePortXP-C6DC-SPP-1'
# Linux usb serial port
COMPORT = '/dev/ttyUSB0'
#COMPORT = '/dev/rfcomm0'
# MacBook Pro usb serial port
#COMPORT = '/dev/tty.PL2303-0000103D'
BAUDRATE=2400
DATABITS=8
PARITY='N'
STOPBITS=1
COMPORT_TIMEOUT=10
TOOLSERVER = 'http://localhost:8008'
from settings_local import *


FIXTURE_DIRS = (
    'fixtures',
)
