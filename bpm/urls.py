from django.urls import path
from django.conf.urls import url
from bpm import views

urlpatterns = [
    path('', views.home, name="home"),
    path('playlist', views.getPlaylist, name="playlist"),
    url(r'analyze/(?P<playlistId>[-.\w]+)/$', views.analyze, name="analyze"),
]
