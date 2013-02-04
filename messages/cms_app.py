from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
__author__ = 'Zhou Guangwen'

class MessagesApp(CMSApp):
    name = _("Messages App")
    urls = ["messages.urls"]

apphook_pool.register(MessagesApp)