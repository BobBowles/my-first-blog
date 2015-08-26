from django.conf.urls import url
from . import views


urlpatterns = [

    # year and month views
    url(r'^(?P<year>\d+)/$', views.year),
    url(r'^$', views.year),                         # default is this year
    url(r'^month/(?P<year>\d+)/(?P<month>\d+)/(?P<change>prev|next)/$',
        views.month,
    ),
    url(r'^month/(?P<year>\d+)/(?P<month>\d+)/$', views.month),
    url(r'^month/$', views.month),                  # default is this month


# slug format multi-day views
    url(
        r'^multi_day/(?P<slug>\d{4}-\d\d-\d\d)/(?P<change>prev|next)/$', 
        views.multi_day
    ),
    url(r'^multi_day/(?P<slug>\d{4}-\d\d-\d\d)/$', views.multi_day),
    url(r'^multi_day/$', views.multi_day),           # default day is today


# slug format day views
    url(
        r'^day/(?P<slug>\d{4}-\d\d-\d\d)/(?P<change>prev|next)/$',
        views.day,
    ),
    url(r'^day/(?P<slug>\d{4}-\d\d-\d\d)/$', views.day),
    url(r'^day/$', views.day),                      # default day is today


# slug format entry views
    url(r'^entry/(?P<slug>\d{4}-\d\d-\d\d_\d\d-\d\d)/$', views.entry,),
    url(r'^entry/(?P<pk>\d+)/$', views.entry),
    url(r'^entry/$', views.entry),                  # default is create new
    url(r'^entry_delete/(?P<pk>\d+)/$', views.entry_delete),


# TODO: for ajax
    url(r'^entry_update/(?P<pk>\d+)/(?P<slug>\d{4}\-\d\d\-\d\d\+\d\d:\d\d)/$', 
        views.entry_update,
    ),
    url(r'^entry_update/(?P<pk>\d+)/(?P<slug>\d\d:\d\d)/$', views.entry_update),
    url(r'^entry_update/$', views.entry_update),    # placeholder


    # the following are redundant and not maintained
    url(
r'^day_list/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<change>prev|next)/$',
views.day_list,
    ),
    url(
        r'^day_list/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 
        views.day_list
    ),
    url(r'^day_list/$', views.day_list),            # default day is today
]

