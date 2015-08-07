from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^(?P<year>[0-9]+)/$', views.main),
    url(r'^$', views.main),
]

