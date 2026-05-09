import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { notificationKeys } from '../keys'
import type {
  GetNotificationsArgs,
  GetNotificationsResponse,
  NotificationSettings,
  UpdateEventConfigPayload,
  UpdateGlobalConfigPayload,
} from '@/api/services/notifications/types'
import { computed, toValue } from 'vue'
import { notificationsService } from '@/api/services/notifications'
import type { MaybeRefArgs, MutationConfig, QueryConfig } from '../types'
import type { AxiosError } from 'axios'
import type { ApiError } from '@/api/errors'

export const useNotifications = (
  payload: MaybeRefArgs<GetNotificationsArgs> = {},
  config?: QueryConfig<GetNotificationsResponse>,
) => {
  const page = computed(() => toValue(payload.page) ?? 1)
  const pageSize = computed(() => toValue(payload.pageSize) ?? 10)

  return useQuery<GetNotificationsResponse, AxiosError<ApiError>>({
    queryKey: computed(() => notificationKeys.list(page.value, pageSize.value)),
    queryFn: () => notificationsService.getNotifications({ page, pageSize }),
    ...config,
  })
}

export const useUnreadCount = (config?: QueryConfig<{ unread_count: number }>) => {
  return useQuery<{ unread_count: number }, AxiosError<ApiError>>({
    queryKey: notificationKeys.unreadCount(),
    queryFn: notificationsService.getUnreadCount,
    refetchInterval: 30000, // Poll every 30s
    ...config,
  })
}

export const useNotificationSettings = (config?: QueryConfig<NotificationSettings>) => {
  return useQuery<NotificationSettings, AxiosError<ApiError>>({
    queryKey: notificationKeys.settings(),
    queryFn: notificationsService.getNotificationSettings,
    ...config,
  })
}

export const useMarkAsRead = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, { id: number }>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, { id: number }>({
    mutationFn: notificationsService.markAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.lists() })
      queryClient.invalidateQueries({ queryKey: notificationKeys.unreadCount() })
    },
    ...config,
  })
}

export const useMarkAllAsRead = (config?: MutationConfig) => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: notificationsService.markAllAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.lists() })
      queryClient.invalidateQueries({ queryKey: notificationKeys.unreadCount() })
    },
    ...config,
  })
}

export const useDeleteNotification = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, { id: number }>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, { id: number }>({
    mutationFn: notificationsService.deleteNotification,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.lists() })
      queryClient.invalidateQueries({ queryKey: notificationKeys.unreadCount() })
    },
    ...config,
  })
}

export const useDeleteAllNotifications = (config?: MutationConfig) => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: notificationsService.deleteAllNotifications,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.lists() })
      queryClient.invalidateQueries({ queryKey: notificationKeys.unreadCount() })
    },
    ...config,
  })
}

export const useUpdateEventConfig = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, UpdateEventConfigPayload>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, UpdateEventConfigPayload>({
    mutationFn: notificationsService.updateEventConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.settings() })
    },
    ...config,
  })
}

export const useUpdateGlobalConfig = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, UpdateGlobalConfigPayload>,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError>, UpdateGlobalConfigPayload>({
    mutationFn: notificationsService.updateGlobalConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.settings() })
    },
    ...config,
  })
}
