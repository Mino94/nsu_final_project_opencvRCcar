from django.contrib import admin
from django.urls import path
import hello.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', hello.views.home, name='home'),
    path('video_feed', hello.views.video_feed, name='video_feed'),
]
