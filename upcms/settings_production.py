__author__ = 'Zhou Guangwen'

import settings

settings.ERP_HOST = "10.100.100.14"
settings.DEBUG = TEMPLATE_DEBUG = False
settings.CAS_SERVER_URL = "http://sso.updis.cn:81/cas/"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
    }
}
