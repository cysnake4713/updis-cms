from django.views.decorators.cache import cache_page
from messages.views import *

__author__ = 'Zhou Guangwen'
from django.conf.urls import patterns, url

urlpatterns = patterns('messages.views',
                       url(r'^$', 'index', name="messages_index"),
                       url(r'^message/(?P<message_id>\d+)/$', 'detail', name="messages_detail"),
                       url(r'^message/vote/like/(?P<message_id>\d+)/$', 'vote_like', name="vote_like"),
                       url(r'^message/vote/unlike/(?P<message_id>\d+)/$', 'vote_unlike', name="vote_unlike"),
                       url(r'^category/(?P<category_id>\d+)/$', 'by_category', name="category_messages"),
                       url(r'^search/(?P<search_context>.+)$', 'search', name='search'),
                       url(r'^image/department/(?P<department_id>\d+)/$', cache_page(60 * 600)(get_department_image),
                           name="get_department_image"),
                       url(r'^image_big/department/(?P<department_id>\d+)/$',
                           cache_page(60 * 600)(get_department_image_big),
                           name="get_department_image_big"),
                       url(r'^image/employee/(?P<employee_id>\d+)/$', get_employee_image,
                           name="get_employee_image"),
                       url(r'^attachment/(?P<attachment_id>\d+)/$', cache_page(60 * 600)(get_attachment),
                           name="get_attachment"),
                       url(r'reload/(?P<TYPE>\d+)/$', reload_cache, name="reload_cache"),
)