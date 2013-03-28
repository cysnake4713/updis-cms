from django.views.decorators.cache import cache_page
from messages.views import get_department_image

__author__ = 'Zhou Guangwen'
from django.conf.urls import patterns, include, url

urlpatterns = patterns('messages.views',
                       url(r'^$', 'index', name="messages_index"),
                       url(r'^login/$', 'login', name="login"),
                       url(r'^message/(?P<message_id>\d+)/$', 'detail', name="messages_detail"),
                       url(r'^category/(?P<category_id>\d+)/$', 'by_category', name="category_messages"),
                       url(r'^image/department/(?P<department_id>\d+)/$', cache_page(60 * 60)(get_department_image),
                           name="get_department_image"),
)