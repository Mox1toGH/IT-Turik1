export interface Notification {
  id: number
  event_type: string
  title: string
  message: string
  is_read: boolean
  created_at: string
}

export interface NotificationSettings {
  event_types: { key: string; title: string }[]
  configs: { event_type: string; is_system_enabled: boolean; is_email_enabled: boolean }[]
  global_config: { emails_disabled_globally: boolean }
}

export interface UnreadCount {
  unread_count: number
}

export interface UpdateEventConfigPayload {
  event_type: string
  is_system_enabled?: boolean
  is_email_enabled?: boolean
}

export interface UpdateGlobalConfigPayload {
  emails_disabled_globally: boolean
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
