from django.conf.urls import url
from . import views
from necloudweather.views import  *
from django.contrib import admin
admin.autodiscover()
urlpatterns = (
    url(r'^$', views.index, name='index'),
    url(r'^results/$', results),
    url(r'^post1/$', post1),
    url(r'^loadregion/$',loadregion),
)
