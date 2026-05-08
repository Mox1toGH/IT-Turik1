from django.urls import path
from .views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    UnreadCountView,
    NotificationDeleteView,
    NotificationDeleteAllView,
    NotificationSettingsView,
    NotificationConfigUpdateView,
    GlobalConfigUpdateView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('<int:pk>/', NotificationDeleteView.as_view(), name='notification-delete'),
    path('read-all/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('delete-all/', NotificationDeleteAllView.as_view(), name='notification-delete-all'),
    path('unread-count/', UnreadCountView.as_view(), name='notification-unread-count'),

    # Personal Settings (Production)
    path('settings/', NotificationSettingsView.as_view(), name='notification-settings'),
    path('settings/config/update/', NotificationConfigUpdateView.as_view(), name='notification-settings-config-update'),
    path('settings/global/update/', GlobalConfigUpdateView.as_view(), name='notification-settings-global-update'),
]
