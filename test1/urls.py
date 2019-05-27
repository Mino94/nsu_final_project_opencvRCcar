from django.contrib import admin
from django.urls import path
import hello.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', hello.views.home, name='home'),
    path('second/', hello.views.second, name='second'),
    path('video_feed', hello.views.video_feed, name='video_feed'),
    path('second_video_feed', hello.views.second_video_feed, name='second_video_feed'),

]
