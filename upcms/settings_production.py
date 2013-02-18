__author__ = 'Zhou Guangwen'
from settings import *

DEBUG = TEMPLATE_DEBUG = True
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '192.168.10.14:11211',
    }
}
