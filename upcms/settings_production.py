__author__ = 'Zhou Guangwen'

from settings import *

ERP_HOST = "10.100.100.14"
DEBUG = TEMPLATE_DEBUG = False
CAS_SERVER_URL = "http://sso.updis.cn:81/cas/"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
    }
}
