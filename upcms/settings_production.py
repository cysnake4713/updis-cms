__author__ = 'Zhou Guangwen'
import  settings
settings.ERP_HOST = "10.100.100.14"



from settings import *
DEBUG = TEMPLATE_DEBUG = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
        }
}
