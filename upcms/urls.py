from django.conf.urls import patterns, include, url
from tastypie.api import Api
from messages.api.resources import MessageResource, CategoryResource
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin

api_v1 = Api()
api_v1.register(MessageResource())
api_v1.register(CategoryResource())

admin.autodiscover()

from cms.sitemaps import CMSSitemap

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'upcms.views.home', name='home'),
                       # url(r'^upcms/', include('upcms.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # url(r'^admin/', include(admin.site.urls)),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^message/', include('messages.urls')),
                       url(r'^account/', include('updisauth.urls')),
                       url(r'^api/', include(api_v1.urls)),
                       url(r'^', include('cms.urls')),
                       url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
                           {'sitemaps': {'cmspages': CMSSitemap}}),
) + staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
                            (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                             {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )