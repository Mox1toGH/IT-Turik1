from django.urls import path
from ..views import TeamMemberInviteView, TeamMemberRemoveView


urlpatterns = [
    path('<int:pk>/members/', TeamMemberInviteView.as_view(), name='team_members'),
    path('<int:pk>/members/<int:user_id>/', TeamMemberRemoveView.as_view(), name='team_member_detail'),
]
