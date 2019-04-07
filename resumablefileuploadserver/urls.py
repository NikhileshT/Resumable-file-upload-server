from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

from upload import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^upload$', views.resumable, name='resumable'),
    url(r'^admin/', admin.site.urls),
]
