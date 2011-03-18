from django.conf.urls.defaults import *
from eventanalyzer import views

urlpatterns = patterns('',
    url(r'^$', views.try_query, name='eventanalyzer_try_query'),
    url(r'^result/$', views.query_result, name='eventanalyzer_query_result'),
)