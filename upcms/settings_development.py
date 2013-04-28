__author__ = 'Zhou Guangwen'
from settings import *

DEBUG = TEMPLATE_DEBUG = True
# CAS_SERVER_URL = "http://sso.updis.cn/cas/"
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
