import { apiClient } from '@/api/client'
import type {
  Notification,
  NotificationSettings,
  UnreadCount,
  UpdateEventConfigPayload,
  UpdateGlobalConfigPayload,
  PaginatedResponse,
} from './types'

const prefix = '/api/notifications'

export const notificationsService = {
  async getNotifications(page: number = 1, pageSize: number = 10) {
    const { data } = await apiClient.get<PaginatedResponse<Notification>>(
      `${prefix}/?page=${page}&page_size=${pageSize}`,
    )
    return data
  },

  async getUnreadCount() {
    const { data } = await apiClient.get<UnreadCount>(`${prefix}/unread-count/`)
    return data
  },

  async getNotificationSettings() {
    const { data } = await apiClient.get<NotificationSettings>(`${prefix}/settings/`)
    return data
  },

  async markAsRead(id: number) {
    const { data } = await apiClient.post(`${prefix}/${id}/read/`)
    return data
  },

  async markAllAsRead() {
    const { data } = await apiClient.post(`${prefix}/read-all/`)
    return data
  },

  async updateEventConfig(payload: UpdateEventConfigPayload) {
    const { data } = await apiClient.post(`${prefix}/settings/config/update/`, payload)
    return data
  },

  async updateGlobalConfig(payload: UpdateGlobalConfigPayload) {
    const { data } = await apiClient.post(`${prefix}/settings/global/update/`, payload)
    return data
  },
}
