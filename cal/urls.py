from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^(?P<year>\d+)/$', views.year),
    url(r'^$', views.year),                         # default is this year
    url(r'^month/(?P<year>\d+)/(?P<month>\d+)/(?P<change>prev|next)/$',
        views.month,
    ),
    url(r'^month/(?P<year>\d+)/(?P<month>\d+)/$', views.month),
    url(r'^month/$', views.month),                  # default is this month
    url(
r'^day/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<change>prev|next)/$',
views.day,
    ),
    url(r'^day/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', views.day),
    url(r'^day/$', views.day),                      # default day is today
    url(
r'^day_list/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<change>prev|next)/$',
views.day_list,
    ),
    url(
        r'^day_list/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 
        views.day_list
    ),
    url(r'^day_list/$', views.day_list),            # default day is today
    url(
r'^entry/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/$', 
views.entry,
    ),
    url(r'^entry/(?P<pk>\d+)/$', views.entry),
    url(r'^entry/$', views.entry),                  # default is create new
    url(r'^entry_delete/(?P<pk>\d+)/$', views.entry_delete),
]

