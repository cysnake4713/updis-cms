from django.views.decorators.cache import cache_page
from messages.views import *

__author__ = 'Zhou Guangwen'
from django.conf.urls import patterns, url

urlpatterns = patterns('vote.views',
                       url(r'votes/$', 'get_votes', name="get_votes"),
                       url(r'votes_record/(?P<vote__category_id>\d+)/$', 'get_votes_record', name='get_votes_record'),
                       url(r'votes_detail/(?P<vote_record_id>\d+)/$', 'get_votes_detail', name='get_votes_detail'),
)