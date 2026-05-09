import { apiClient } from '@/api/client'
import { toValue } from 'vue'
import type {
  GetNotificationsArgs,
  GetNotificationsResponse,
  NotificationSettings,
  UnreadCount,
  UpdateEventConfigPayload,
  UpdateGlobalConfigPayload,
} from './types'
import type { MaybeRefArgs } from '@/api/queries/types'

const prefix = '/api/notifications'

export const notificationsService = {
  async getNotifications(args: MaybeRefArgs<GetNotificationsArgs> = {}) {
    const page = toValue(args.page) ?? 1
    const pageSize = toValue(args.pageSize) ?? 10

    const { data } = await apiClient.get<GetNotificationsResponse>(
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

  async markAsRead(args: MaybeRefArgs<{ id: number }>) {
    const { data } = await apiClient.post(`${prefix}/${toValue(args.id)}/read/`)
    return data
  },

  async markAllAsRead() {
    const { data } = await apiClient.post(`${prefix}/read-all/`)
    return data
  },

  async deleteNotification(args: MaybeRefArgs<{ id: number }>) {
    const { data } = await apiClient.delete(`${prefix}/${toValue(args.id)}/`)
    return data
  },

  async deleteAllNotifications() {
    const { data } = await apiClient.delete(`${prefix}/delete-all/`)
    return data
  },

  async updateEventConfig(payload: MaybeRefArgs<UpdateEventConfigPayload>) {
    const { data } = await apiClient.post(`${prefix}/settings/config/update/`, {
      event_type: toValue(payload.event_type),
      is_system_enabled: toValue(payload.is_system_enabled),
      is_email_enabled: toValue(payload.is_email_enabled),
    })
    return data
  },

  async updateGlobalConfig(payload: MaybeRefArgs<UpdateGlobalConfigPayload>) {
    const { data } = await apiClient.post(`${prefix}/settings/global/update/`, {
      emails_disabled_globally: toValue(payload.emails_disabled_globally),
    })
    return data
  },
}
