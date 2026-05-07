# Notifications API Cheat Sheet

This document outlines the API endpoints for the notification system, including retrieval, management, and personal settings.

---

### 1. Notification Management

| Action | Method | Path | Access |
| :--- | :--- | :--- | :--- |
| **List Notifications** | GET | `/api/notifications/` | Authenticated |
| **Mark as Read** | POST | `/api/notifications/{id}/read/` | Recipient |
| **Mark All as Read** | POST | `/api/notifications/read-all/` | Authenticated |
| **Unread Count** | GET | `/api/notifications/unread-count/` | Authenticated |

#### Get Notifications — `GET /api/notifications/`
Returns a list of notifications for the current user, ordered by newest first.
```json
[
  {
    "id": 12,
    "event_type": "team_invitation",
    "title": "New Team Invitation",
    "message": "Admin has invited you to join Test Team",
    "is_read": false,
    "created_at": "2026-04-30T10:00:00Z"
  }
]
```

#### Mark All as Read — `POST /api/notifications/read-all/`
Response:
```json
{
  "marked": 5
}
```

#### Unread Count — `GET /api/notifications/unread-count/`
Response:
```json
{
  "unread_count": 3
}
```

---

### 2. Personal Notification Settings

Every user can customize which notifications they receive and through which channels.

| Action | Method | Path | Access |
| :--- | :--- | :--- | :--- |
| **Get My Settings** | GET | `/api/notifications/settings/` | Authenticated |
| **Update Event Config** | POST | `/api/notifications/settings/config/update/` | Authenticated |
| **Update Global Email** | POST | `/api/notifications/settings/global/update/` | Authenticated |

#### Get My Settings — `GET /api/notifications/settings/`
Returns available event types and the user's personal configuration for each.
```json
{
  "event_types": [
    { "key": "team_invitation", "title": "Team Invitation" },
    { "key": "tournament_start", "title": "Tournament Start" }
  ],
  "configs": [
    {
      "event_type": "team_invitation",
      "is_system_enabled": true,
      "is_email_enabled": true
    }
  ],
  "global_config": {
    "emails_disabled_globally": false
  }
}
```

#### Update Event Config — `POST /api/notifications/settings/config/update/`
Enables or disables a specific channel for a specific event type.
**Request Body:**
```json
{
  "event_type": "team_invitation",
  "is_system_enabled": true,
  "is_email_enabled": false
}
```

#### Update Global Email Toggle — `POST /api/notifications/settings/global/update/`
The "Master Switch" to disable all notification emails for your account.
**Request Body:**
```json
{
  "emails_disabled_globally": true
}
```

---

### 3. Implementation Notes
- **Personalization**: Users only have access to their own settings. Even Admins cannot modify notification preferences for other users.
- **Auto-Initialization**: When a user first accesses the settings, the system automatically creates their default configuration based on the system defaults.
- **Channels**:
    - **System**: Visible in the in-app notification center.
    - **Email**: Sent to the user's registered email address (can be disabled globally or per event).
