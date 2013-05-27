from django.views.decorators.cache import cache_page
from messages.views import *

__author__ = 'Zhou Guangwen'
from django.conf.urls import patterns, url

urlpatterns = patterns('messages.views',
                       url(r'^$', 'index', name="messages_index"),
                       url(r'^message/(?P<message_id>\d+)/$', 'detail', name="messages_detail"),
                       url(r'^category/(?P<category_id>\d+)/$', 'by_category', name="category_messages"),
                       url(r'^search/(?P<search_context>.+)$', 'search', name='search'),
                       url(r'^image/department/(?P<department_id>\d+)/$', cache_page(60 * 600)(get_department_image),
                           name="get_department_image"),
                       url(r'^image_big/department/(?P<department_id>\d+)/$',
                           cache_page(60 * 600)(get_department_image_big),
                           name="get_department_image_big"),
                       url(r'^image/employee/(?P<employee_id>\d+)/$', cache_page(60 * 600)(get_employee_image),
                           name="get_employee_image"),
                       url(r'^attachment/(?P<attachment_id>\d+)/$', cache_page(60 * 600)(get_attachment),
                           name="get_attachment"),
                       url(r'reload/(?P<TYPE>\d+)/$', reload_cache, name="reload_cache"),
                       url(r'votes/$', 'get_votes', name="get_votes"),
                       url(r'votes_record/(?P<vote__category_id>\d+)/$', 'get_votes_record', name='get_votes_record'),
                       url(r'votes_detail/(?P<vote_record_id>\d+)/$', 'get_votes_detail', name='get_votes_detail'),
                       url(r'^image/(?P<model>.+)/(?P<field>.+)/(?P<id>\d+)/$', cache_page(60 * 600)(get_image),
                           name="get_image"),
)