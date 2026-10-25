import { computed, ref, type ComputedRef, type Ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  useDeleteAllNotifications,
  useDeleteNotification,
  useGetUnreadNotificationCount,
  useListNotifications,
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
} from '@/api/notifications/notifications'
import type { NotificationResponse } from '@/api/backendAPINinja.schemas'
import { useNotification } from '@/composables/useNotification'
import type { QueryLike } from '@/composables/useQueryState'

export interface NotificationMessagePart {
  type: string
  id?: string
  text: string
}

export interface NotificationConfirmConfig {
  title: string
  scope: 'single' | 'all'
  onConfirm: () => void
  confirmVariant: 'danger'
}

export function getNotificationRedirectUrl(notification: NotificationResponse): string | null {
  const type = notification.event_type

  // Only invitations go to /teams — recipient hasn't joined yet
  if (type === 'team_invitation_received') {
    return '/teams'
  }

  if (type.startsWith('team_')) {
    // Other team events can still link directly if possible
    const match = notification.message.match(/\[team:(\d+):.+?\]/)
    if (match) {
      return `/teams/${match[1]}`
    }
    return '/teams'
  }
  if (type === 'news_published') {
    const match = notification.message.match(/\[news:(\d+):.+?\]/)
    if (match) {
      return `/news#news-${match[1]}`
    }
    return '/news'
  }
  if (type.startsWith('tournament_')) {
    return '/tournaments'
  }
  if (type === 'jury_assignment_received') {
    return '/evaluation'
  }
  return null
}

export function parseNotificationMessage(message: string): NotificationMessagePart[] {
  const parts: NotificationMessagePart[] = []
  // Matches [user:id:name], [team:id:name], or [news:id:title]
  const regex = /\[(user|team|news):(\d+):(.+?)\]/g
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = regex.exec(message)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', text: message.substring(lastIndex, match.index) })
    }
    parts.push({
      type: match[1]!,
      id: match[2],
      text: match[3]!,
    })
    lastIndex = regex.lastIndex
  }

  if (lastIndex < message.length) {
    parts.push({ type: 'text', text: message.substring(lastIndex) })
  }

  return parts.length > 0 ? parts : [{ type: 'text', text: message }]
}

export function formatNotificationDate(dateStr: string): string {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export function formatNotificationEventType(eventType: string): string {
  return eventType
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const NOTIFICATION_CATEGORY_PREFIXES: { prefix: string; label: string }[] = [
  { prefix: 'team_', label: 'Teams' },
  { prefix: 'tournament_', label: 'Tournaments' },
  { prefix: 'round_', label: 'Rounds' },
  { prefix: 'submission_', label: 'Submissions' },
  { prefix: 'jury_', label: 'Evaluation' },
  { prefix: 'evaluation_', label: 'Evaluation' },
  { prefix: 'news_', label: 'News' },
]

export function getNotificationCategory(eventType: string): string {
  const match = NOTIFICATION_CATEGORY_PREFIXES.find(({ prefix }) => eventType.startsWith(prefix))
  return match?.label ?? 'Updates'
}

export interface UseNotificationsOptions {
  page?: Ref<number> | ComputedRef<number>
}

export interface UseNotificationsReturn {
  /** Query state consumed by `UiQueryBlock` for loading, error, and empty handling. */
  query: QueryLike
  notificationsData: Ref<{ items: NotificationResponse[]; count: number } | undefined>
  unreadCount: Ref<{ unread_count: number } | undefined>
  unreadNotifications: ComputedRef<NotificationResponse[]>
  hasUnread: ComputedRef<boolean>
  hasNotifications: ComputedRef<boolean>
  totalPages: ComputedRef<number>
  isMarkingAll: Ref<boolean>
  isDeletingAll: Ref<boolean>
  isConfirmModalOpen: Ref<boolean>
  confirmModalConfig: Ref<NotificationConfirmConfig>
  markAsRead: (params: { notificationId: number }) => void
  handleMarkRead: (id: number) => void
  handleMarkAllRead: () => void
  requestDeleteConfirm: (id: number) => void
  requestDeleteAllConfirm: () => void
  handleNotificationClick: (notification: NotificationResponse) => void
}

export function useNotifications(options?: UseNotificationsOptions): UseNotificationsReturn {
  const router = useRouter()
  const { showNotification } = useNotification()

  const listParams =
    options?.page !== undefined ? computed(() => ({ page: options.page!.value })) : undefined
  const notificationsQuery = useListNotifications(listParams)
  const { data: notificationsData } = notificationsQuery
  const { data: unreadCount } = useGetUnreadNotificationCount()
  const { mutate: markAsRead } = useMarkNotificationRead()
  const { mutate: markAllAsRead, isPending: isMarkingAll } = useMarkAllNotificationsRead()
  const { mutate: deleteNotification } = useDeleteNotification()
  const { mutate: deleteAllNotifications, isPending: isDeletingAll } = useDeleteAllNotifications()

  const isConfirmModalOpen = ref(false)
  const confirmModalConfig = ref<NotificationConfirmConfig>({
    title: '',
    scope: 'single',
    onConfirm: () => {},
    confirmVariant: 'danger',
  })

  const unreadNotifications = computed(() => {
    return notificationsData.value?.items.filter((n) => !n.is_read) || []
  })

  const hasUnread = computed(() => unreadNotifications.value.length > 0)
  const hasNotifications = computed(() => (notificationsData.value?.items.length ?? 0) > 0)

  const totalPages = computed(() => {
    if (!notificationsData.value?.count) return 1
    return Math.ceil(notificationsData.value.count / 10)
  })

  const markAsReadNotification = (params: { notificationId: number }): void => {
    markAsRead(params)
  }

  const handleMarkRead = (id: number): void => {
    markAsReadNotification({ notificationId: id })
  }

  const handleMarkAllRead = (): void => {
    markAllAsRead(void 0, {
      onSuccess: () => showNotification('All notifications marked as read', 'success'),
      onError: (error) => showNotification(error.message, 'error'),
    })
  }

  const requestDeleteConfirm = (id: number): void => {
    confirmModalConfig.value = {
      title: 'Delete Notification',
      scope: 'single',
      confirmVariant: 'danger',
      onConfirm: () => {
        deleteNotification(
          { notificationId: id },
          {
            onSuccess: () => {
              showNotification('Notification deleted', 'success')
              isConfirmModalOpen.value = false
            },
          },
        )
      },
    }
    isConfirmModalOpen.value = true
  }

  const requestDeleteAllConfirm = (): void => {
    confirmModalConfig.value = {
      title: 'Delete All Notifications',
      scope: 'all',
      confirmVariant: 'danger',
      onConfirm: () => {
        deleteAllNotifications(undefined, {
          onSuccess: () => {
            showNotification('All notifications deleted', 'success')
            isConfirmModalOpen.value = false
          },
          onError: (error) => {
            showNotification(error.message, 'error')
          },
        })
      },
    }
    isConfirmModalOpen.value = true
  }

  const handleNotificationClick = (notification: NotificationResponse): void => {
    if (!notification.is_read) {
      handleMarkRead(notification.id)
    }

    const url = getNotificationRedirectUrl(notification)
    if (url) {
      router.push(url)
    }
  }

  return {
    query: notificationsQuery,
    notificationsData: notificationsData as UseNotificationsReturn['notificationsData'],
    unreadCount: unreadCount as UseNotificationsReturn['unreadCount'],
    unreadNotifications,
    hasUnread,
    hasNotifications,
    totalPages,
    isMarkingAll,
    isDeletingAll,
    isConfirmModalOpen,
    confirmModalConfig,
    markAsRead: markAsReadNotification,
    handleMarkRead,
    handleMarkAllRead,
    requestDeleteConfirm,
    requestDeleteAllConfirm,
    handleNotificationClick,
  }
}
