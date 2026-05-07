import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { notificationKeys } from '../keys'
import type {
  Notification,
  NotificationSettings,
  UpdateEventConfigPayload,
  UpdateGlobalConfigPayload,
  PaginatedResponse,
} from '@/api/services/notifications/types'
import { type Ref, unref, computed } from 'vue'
import { notificationsService } from '@/api/services/notifications'

export const useNotifications = (
  page: Ref<number> | number = 1,
  pageSize: Ref<number> | number = 10,
) => {
  return useQuery({
    queryKey: computed(() => notificationKeys.list(unref(page), unref(pageSize))),
    queryFn: async (): Promise<PaginatedResponse<Notification>> => {
      return await notificationsService.getNotifications(unref(page), unref(pageSize))
    },
  })
}

export const useUnreadCount = () => {
  return useQuery({
    queryKey: notificationKeys.unreadCount(),
    queryFn: async (): Promise<{ unread_count: number }> => {
      return await notificationsService.getUnreadCount()
    },
    refetchInterval: 30000, // Poll every 30s
  })
}

export const useNotificationSettings = () => {
  return useQuery({
    queryKey: notificationKeys.settings(),
    queryFn: async (): Promise<NotificationSettings> => {
      return await notificationsService.getNotificationSettings()
    },
  })
}

export const useMarkAsRead = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      return await notificationsService.markAsRead(id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.lists() })
      queryClient.invalidateQueries({ queryKey: notificationKeys.unreadCount() })
    },
  })
}

export const useMarkAllAsRead = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      return await notificationsService.markAllAsRead()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.lists() })
      queryClient.invalidateQueries({ queryKey: notificationKeys.unreadCount() })
    },
  })
}

export const useUpdateEventConfig = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: UpdateEventConfigPayload) => {
      return await notificationsService.updateEventConfig(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.settings() })
    },
  })
}

export const useUpdateGlobalConfig = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: UpdateGlobalConfigPayload) => {
      return await notificationsService.updateGlobalConfig(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.settings() })
    },
  })
}
