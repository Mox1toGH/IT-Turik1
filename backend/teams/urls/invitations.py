from django.urls import path

from ..views import (
    TeamInvitationAcceptView,
    TeamInvitationDeclineView,
    TeamInvitationListView,
    TeamInvitationListByTeamView,
)

urlpatterns = [
    path('invitations/', TeamInvitationListView.as_view(), name='team_invitations'),
    path(
        'invitations/<int:invitation_id>/accept/',
        TeamInvitationAcceptView.as_view(),
        name='team_invitation_accept',
    ),
    path(
        'invitations/<int:invitation_id>/decline/',
        TeamInvitationDeclineView.as_view(),
        name='team_invitation_decline',
    ),
    path('<int:pk>/invitations/', TeamInvitationListByTeamView.as_view(), name='team_invitations_by_team'),
]