from django.urls import path

from .consumers import LeaderboardConsumer

websocket_urlpatterns = [
    path("ws/leaderboards/", LeaderboardConsumer.as_asgi()),
]

