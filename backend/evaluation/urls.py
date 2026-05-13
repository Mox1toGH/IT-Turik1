from django.urls import path
from .views import (
    AvailableJuryListView,
    JuryAssignmentDetailView,
    JuryAssignmentListView,
    JuryEvaluationCreateView,
    JuryEvaluationDetailView,
    AdminRoundAssignmentView,
    RoundLeaderboardView,
    RoundPassingStatusView,
    TournamentLeaderboardView,
    TournamentLeaderboardGoogleSheetsExportView,
)

urlpatterns = [
    path('assignments/', JuryAssignmentListView.as_view(), name='jury_assignments'),
    path(
        'assignments/<int:pk>/',
        JuryAssignmentDetailView.as_view(),
        name='jury_assignment_detail',
    ),
    path('evaluate/<int:pk>/', JuryEvaluationDetailView.as_view(), name='jury_evaluate'),
    path('evaluate/', JuryEvaluationCreateView.as_view(), name='jury_evaluate_create'),
    path('rounds/<int:pk>/assign-jury/', AdminRoundAssignmentView.as_view(), name='round_assign_jury'),
    path('rounds/<int:pk>/available-jury/', AvailableJuryListView.as_view(), name='round_available_jury'),
    path('tournaments/rounds/<int:round_id>/leaderboard/', RoundLeaderboardView.as_view(), name='round_leaderboard'),
    path('rounds/<int:pk>/passing-status/', RoundPassingStatusView.as_view(), name='round_passing_status'),
    path('tournaments/<int:tournament_id>/leaderboard/', TournamentLeaderboardView.as_view(), name='tournament_leaderboard'),
    path(
        'tournaments/<int:tournament_id>/leaderboard/export/google-sheets/',
        TournamentLeaderboardGoogleSheetsExportView.as_view(),
        name='tournament_leaderboard_google_sheets_export',
    ),
]
