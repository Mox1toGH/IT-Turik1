from django.urls import path

from ..views import (
    TeamBannerView,
    TeamDetailView,
    TeamLeaveView,
    TeamListCreateView,
    TeamMemberInviteView,
    TeamMemberRemoveView,
)
from .invitations import urlpatterns as invitation_urls
from .join_requests import urlpatterns as join_request_urls

urlpatterns = [
    path('', TeamListCreateView.as_view(), name='teams'),
    path('<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('<int:pk>/banner/', TeamBannerView.as_view(), name='team_banner'),
    path('<int:pk>/leave/', TeamLeaveView.as_view(), name='team_leave'),
    path('<int:pk>/members/', TeamMemberInviteView.as_view(), name='team_members'),
    path('<int:pk>/members/<int:user_id>/', TeamMemberRemoveView.as_view(), name='team_member_detail'),
    *invitation_urls,
    *join_request_urls,
]
