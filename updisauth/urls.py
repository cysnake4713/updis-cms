from django.conf.urls import patterns, url

__author__ = 'cysnake4713'

urlpatterns = patterns('updisauth.views',
                       url(r'^login/$', 'erp_login', name="erp_login"),
                       url(r'^logout/$','erp_logout',name='erp_logout'),
)
