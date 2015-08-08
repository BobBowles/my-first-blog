from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^(?P<year>[0-9]+)/$', views.year),
    url(r'^$', views.year),
    url(r'^month/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<change>prev|next)/$', 
        views.month),
    url(r'^month/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', views.month),
    url(r'^month/$', views.month),
]

