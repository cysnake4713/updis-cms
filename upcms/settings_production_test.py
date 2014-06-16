__author__ = 'Zhou Guangwen'

import settings

settings.ERP_HOST = "10.100.100.171"
# settings.ERP_HOST = "localhost"
settings.DEBUG = TEMPLATE_DEBUG = True
settings.CAS_SERVER_URL = "http://sso.updis.cn/cas/"
settings.ERP_DOMAIN = ".updis.cn"
settings.ERP_HOME = 'http://terp.updis.cn'

settings.DB_HOST = "10.100.100.172"
settings.DB_NAME = "develop"
settings.DB_USER = "openerp_updis"
settings.DB_PASSWORD = "openerpupdis2013"
settings.DB_PORT = "5432"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
    }
}

from settings import *

