from datetime import datetime

from ninja import Schema

class DetailResponse(Schema):
    detail: str


class NotificationResponse(Schema):
    id: int
    event_type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime


class MarkedCountResponse(Schema):
    marked: int


class UnreadCountResponse(Schema):
    unread_count: int


class DeletedCountResponse(Schema):
    deleted: int


class EventTypeResponse(Schema):
    key: str
    title: str


class NotificationConfigResponse(Schema):
    event_type: str
    is_system_enabled: bool
    is_email_enabled: bool


class GlobalConfigResponse(Schema):
    emails_disabled_globally: bool


class NotificationSettingsResponse(Schema):
    event_types: list[EventTypeResponse]
    configs: list[NotificationConfigResponse]
    global_config: GlobalConfigResponse


class NotificationConfigUpdateRequest(Schema):
    event_type: str
    is_system_enabled: bool | None = None
    is_email_enabled: bool | None = None


class GlobalConfigUpdateRequest(Schema):
    emails_disabled_globally: bool
