import os

DEBUG = True

PRODUCTION = False

SECRET_KEY = 'o3&g^gsc=+8+mw49gdv447xg1c1%$*$raz)=(!!7n8t&9gx*py'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = ['127.0.0.1']

STATIC_ROOT = BASE_DIR + "/swegram_main/static/swegram_main"
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'swegram_main/static'),)

MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'swegram_main/uploads')

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
        'NAME': "swegram",
        'USER': os.environ['USER'],
        'PASSWORD': os.environ['POSTGRESPW'],
        'HOST': "localhost",
        'PORT': "5432"
    }
}

CACHES = {
    'default': {
        #'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'swegram-prod',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 8 * 60 * 60
SESSION_SAVE_EVERY_REQUEST = True
