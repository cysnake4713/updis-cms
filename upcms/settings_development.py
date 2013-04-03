__author__ = 'Zhou Guangwen'
from settings import *

DEBUG = TEMPLATE_DEBUG = True
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
