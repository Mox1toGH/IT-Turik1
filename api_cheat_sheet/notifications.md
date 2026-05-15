# Notifications API Cheat Sheet

This document describes notifications over REST and WebSocket.

## 1. REST (Source of Truth)

REST/OpenAPI remains the source of truth for CRUD and initial loading.

| Action | Method | Path | Access |
| :--- | :--- | :--- | :--- |
| List Notifications | GET | `/api/notifications/` | Authenticated |
| Mark as Read | POST | `/api/notifications/{id}/read/` | Recipient |
| Mark All as Read | POST | `/api/notifications/read-all/` | Authenticated |
| Delete Notification | DELETE | `/api/notifications/{id}/` | Recipient |
| Delete All Notifications | DELETE | `/api/notifications/delete-all/` | Authenticated |
| Unread Count | GET | `/api/notifications/unread-count/` | Authenticated |

## 2. WebSocket (Realtime Events Only)

WebSocket is only for realtime updates and does not replace REST.

### Socket URL

- `ws://localhost:8000/ws/notifications/?token=<JWT_ACCESS_TOKEN>`
- Use `wss://` in HTTPS environments.

### Authentication

- JWT access token in query parameter `token`.
- Unauthenticated/invalid token connections are closed (`4401`).
- Each connection is bound to one authenticated user.

### User Isolation

- Events are sent to per-user groups (`notifications.user.<user_id>`).
- A user receives only their own notification events.

### Event Envelope

All messages follow:

```json
{
  "event": "notification.created",
  "payload": {}
}
```

### Event Names and Payloads

1. `notification.created`

```json
{
  "event": "notification.created",
  "payload": {
    "notification": {
      "id": 12,
      "event_type": "team_invitation_received",
      "title": "New Team Invitation",
      "message": "...",
      "is_read": false,
      "created_at": "2026-05-15T12:00:00Z"
    }
  }
}
```

2. `notification.unread_count_updated`

```json
{
  "event": "notification.unread_count_updated",
  "payload": {
    "unread_count": 3
  }
}
```

3. `notification.read_status_changed`

```json
{
  "event": "notification.read_status_changed",
  "payload": {
    "notification_ids": [12, 11],
    "is_read": true
  }
}
```

4. `notification.deleted`

```json
{
  "event": "notification.deleted",
  "payload": {
    "notification_ids": [10]
  }
}
```

## 3. Reconnect Behavior

- Frontend reconnects automatically with exponential backoff.
- Reconnect attempts stop when user logs out or token is removed.
- After reconnect, realtime updates resume from new events; REST can still be used to refresh state if needed.

## 4. Implementation Notes

- Multiple tabs stay synchronized through shared backend events.
- Read/unread counters update instantly via `notification.unread_count_updated`.
- Keep using OpenAPI-generated REST client for initial list loading and CRUD operations.
