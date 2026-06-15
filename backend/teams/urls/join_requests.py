from django.urls import path

from ..views import (
    TeamJoinRequestAcceptView,
    TeamJoinRequestCreateView,
    TeamJoinRequestDeclineView,
    TeamJoinRequestListByTeamView,
)

urlpatterns = [
    path('<int:pk>/join-requests/', TeamJoinRequestCreateView.as_view(), name='team_join_request_create'),
    path(
        '<int:pk>/join-requests/<int:request_id>/accept/',
        TeamJoinRequestAcceptView.as_view(),
        name='team_join_request_accept',
    ),
    path(
        '<int:pk>/join-requests/<int:request_id>/decline/',
        TeamJoinRequestDeclineView.as_view(),
        name='team_join_request_decline',
    ),
    path('<int:pk>/join-requests-list/', TeamJoinRequestListByTeamView.as_view(), name='team_join_requests_list'),
]