from django.urls import path

from .views import AdminStatsView, PlayerStatsView, TeamStatsView, TournamentStatsView

urlpatterns = [
    path('player/', PlayerStatsView.as_view(), name='stats-player'),
    path('team/<int:team_id>/', TeamStatsView.as_view(), name='stats-team'),
    path('tournament/<int:tournament_id>/', TournamentStatsView.as_view(), name='stats-tournament'),
    path('admin/', AdminStatsView.as_view(), name='stats-admin'),
]
