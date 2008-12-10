from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from greetingsweb.admin import site

urlpatterns = patterns('',
    # Example:
    (r'', include('greetingsweb.greetings.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', site.root),
    
)

if settings.LOCAL:
    urlpatterns += patterns('',
        (r'^greetmedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/mkrieger/Dropbox/193P Final Project/greetingsweb/media'}),)
