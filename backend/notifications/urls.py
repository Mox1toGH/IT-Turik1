from django.urls import path
from .views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    UnreadCountView,
    NotificationSettingsView,
    NotificationConfigUpdateView,
    GlobalConfigUpdateView,
)
from .debug_views import (
    NotificationDebugInfoView, 
    NotificationDebugSendView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('read-all/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('unread-count/', UnreadCountView.as_view(), name='notification-unread-count'),
    
    # Personal Settings (Production)
    path('settings/', NotificationSettingsView.as_view(), name='notification-settings'),
    path('settings/config/update/', NotificationConfigUpdateView.as_view(), name='notification-settings-config-update'),
    path('settings/global/update/', GlobalConfigUpdateView.as_view(), name='notification-settings-global-update'),
    
    # Debug endpoints (Admin only)
    path('debug/info/', NotificationDebugInfoView.as_view(), name='notification-debug-info'),
    path('debug/send/', NotificationDebugSendView.as_view(), name='notification-debug-send'),
]
