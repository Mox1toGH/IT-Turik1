from django.urls import path
from .views import (
    AvailableJuryListView,
    JuryAssignmentListView,
    JuryEvaluationCreateView,
    JuryEvaluationDetailView,
    AdminRoundAssignmentView,
    RoundLeaderboardView,
    TournamentLeaderboardView,
)

urlpatterns = [
    path('assignments/', JuryAssignmentListView.as_view(), name='jury_assignments'),
    path('evaluate/<int:assignment_id>/', JuryEvaluationDetailView.as_view(), name='jury_evaluate'),
    path('evaluate/', JuryEvaluationCreateView.as_view(), name='jury_evaluate_create'),
    path('rounds/<int:pk>/assign-jury/', AdminRoundAssignmentView.as_view(), name='round_assign_jury'),
    path('rounds/<int:pk>/available-jury/', AvailableJuryListView.as_view(), name='round_available_jury'),
    path('tournaments/rounds/<int:round_id>/leaderboard/', RoundLeaderboardView.as_view(), name='round_leaderboard'),
    path('tournaments/<int:tournament_id>/leaderboard/', TournamentLeaderboardView.as_view(), name='tournament_leaderboard'),
]
