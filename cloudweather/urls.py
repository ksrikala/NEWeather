from django.conf.urls import patterns, include, url
from django.contrib import admin
from . import views
from cloudweather.views import  *
from necloudweather.views import  *
admin.autodiscover()
urlpatterns = (
	url(r'^$', home_page),
	url(r'^profile/$', user_profile),
	url(r'^tempload/$', tempload),
	url(r'^tempdelete/$', tempdelete),
	url(r'^tempcheck/$', tempcheck),
	url(r'^login/$', user_login),
	url(r'^logout/$', user_logout),
	url(r'^registration/$', signup),
	url(r'^necloudweather/', include('necloudweather.urls')),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^post1/$', post1),
	url(r'^results/$', results),
	url(r'^profilerun/$', profilerun),
        url('', include('social.apps.django_app.urls', namespace='social')),
        url('', include('django.contrib.auth.urls', namespace='auth')),
	url(r'^rimismatch/$', RI),
	url(r'^cpu-utlization/$', cpu),
	#url(r'^output/$', return_data),
)
