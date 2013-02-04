__author__ = 'Zhou Guangwen'
from django.conf.urls import patterns, include, url

urlpatterns = patterns('messages.views',
    url(r'^$', 'index',name="messages_index"),
    url(r'^(?P<message_id>\d+)/$', 'detail',name="messages_detail"),
    url(r'^category/(?P<category_id>\d+)/$','by_category',name="category_messages"),
)