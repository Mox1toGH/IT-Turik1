from django.urls import path

from ..views import (
    TeamBannerView,
    TeamDetailView,
    TeamLeaveView,
    TeamListCreateView,
)


urlpatterns = [
    path('', TeamListCreateView.as_view(), name='teams'),
    path('<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('<int:pk>/banner/', TeamBannerView.as_view(), name='team_banner'),
    path('<int:pk>/leave/', TeamLeaveView.as_view(), name='team_leave'),
]
