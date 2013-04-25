__author__ = 'Zhou Guangwen'

import settings

settings.ERP_HOST = "erp.updis.cn"
settings.DEBUG = TEMPLATE_DEBUG = False
settings.CAS_SERVER_URL = "http://sso.updis.cn/cas/"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
    }
}
