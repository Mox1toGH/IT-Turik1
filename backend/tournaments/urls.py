from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CurrentTaskView,
    EventViewSet,
    IconListView,
    RoundCloseSubmissionsView,
    RoundDetailView,
    RoundListCreateView,
    RoundMarkEvaluatedView,
    RoundStartView,
    SubmissionDetailView,
    SubmissionListCreateView,
    TeamActiveTournamentView,
    TournamentCreateView,
    TournamentDetailView,
    TournamentListView,
    TournamentTeamsView,
    TournamentEligibleTeamsView,
    TournamentStartRegistrationView,
    TournamentTeamRegistrationCreateView,
    TournamentTeamRegistrationDetailView,
    TournamentUpdateView,
    
    TournamentSubmissionsView, 
    RoundSubmissionsView,
)

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', TournamentListView.as_view(), name='tournaments'),
    path('<int:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
    path('manage/', TournamentCreateView.as_view(), name='tournament_manage_create'),
    path('manage/<int:pk>/', TournamentUpdateView.as_view(), name='tournament_manage_update'),
    path(
        '<int:pk>/start-registration/',
        TournamentStartRegistrationView.as_view(),
        name='tournament_start_registration',
    ),
    path('<int:pk>/register-team/', TournamentTeamRegistrationCreateView.as_view(), name='tournament_register_team'),
    path('<int:pk>/eligible-teams/', TournamentEligibleTeamsView.as_view(), name='tournament_eligible_teams'),
    path('<int:pk>/teams/', TournamentTeamsView.as_view(), name='tournament_teams'),
    path('active/', TeamActiveTournamentView.as_view(), name='team_active_tournament'),
    path(
        '<int:pk>/registrations/<int:registration_pk>/',
        TournamentTeamRegistrationDetailView.as_view(),
        name='tournament_registration_detail',
    ),
    path('<int:tournament_pk>/rounds/', RoundListCreateView.as_view(), name='rounds'),
    path('rounds/<int:pk>/', RoundDetailView.as_view(), name='round_detail'),
    path('rounds/<int:pk>/start/', RoundStartView.as_view(), name='round_start'),
    path('rounds/<int:pk>/close-submissions/', RoundCloseSubmissionsView.as_view(), name='round_close_submissions'),
    path('rounds/<int:pk>/mark-evaluated/', RoundMarkEvaluatedView.as_view(), name='round_mark_evaluated'),
    path('submissions/', SubmissionListCreateView.as_view(), name='submissions'),
    path('submissions/<int:pk>/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('<int:pk>/submissions/', TournamentSubmissionsView.as_view(), name='tournament_submissions'),
    path('rounds/<int:pk>/submissions/', RoundSubmissionsView.as_view(), name='round_submissions'),
    
    path('current-task/', CurrentTaskView.as_view(), name='current_task'),
    path('icons/', IconListView.as_view(), name='icon_list'),
] + router.urls
