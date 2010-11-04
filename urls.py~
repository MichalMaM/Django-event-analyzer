from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('eventtracker.urls')),
    (r'^statistics/', include('eventanalyzer.urls')),
    (r'^admin/', include(admin.site.urls)),
)
