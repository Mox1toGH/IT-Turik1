import { computed, reactive, readonly } from 'vue'

const DEFAULT_DURATION_MS = 4200

type NotificationType = 'success' | 'error'

interface NotificationPayload {
  message: string
  type: NotificationType
  duration: number
}

interface NotificationState {
  message: string
  type: NotificationType
  duration: number
  id: number
}

interface GlobalNotificationState {
  current: NotificationState | null
  queue: NotificationPayload[]
}

interface ShowNotificationOptions {
  duration?: number
  mode?: 'queue' | 'replace'
}

const state = reactive<GlobalNotificationState>({
  current: null,
  queue: [],
})

let notificationId = 0
let notificationTimerId: ReturnType<typeof setTimeout> | null = null

const clearNotificationTimer = (): void => {
  if (notificationTimerId) {
    clearTimeout(notificationTimerId)
    notificationTimerId = null
  }
}

const sameNotification = (
  first: NotificationPayload | NotificationState | null | undefined,
  second: NotificationPayload | null,
): boolean =>
  Boolean(first) &&
  Boolean(second) &&
  first!.message === second!.message &&
  first!.type === second!.type

const scheduleDismiss = (duration: number): void => {
  clearNotificationTimer()
  notificationTimerId = setTimeout(() => {
    notificationTimerId = null
    if (state.queue.length > 0) {
      const next = state.queue.shift()!
      showNow(next)
      return
    }
    state.current = null
  }, duration)
}

const showNow = (payload: NotificationPayload): void => {
  state.current = { ...payload, id: ++notificationId }
  scheduleDismiss(payload.duration)
}

const clearNotification = (clearQueue = false): void => {
  clearNotificationTimer()
  if (clearQueue) {
    state.queue.length = 0
    state.current = null
    return
  }
  if (state.queue.length > 0) {
    const next = state.queue.shift()!
    showNow(next)
    return
  }
  state.current = null
}

const showNotification = (
  message?: string,
  type: NotificationType = 'success',
  options?: ShowNotificationOptions,
): void => {
  const text = String(message || '').trim()
  if (!text) return

  if (notification.value) clearNotification()

  const payload: NotificationPayload = {
    message: text,
    type,
    duration: options?.duration ?? DEFAULT_DURATION_MS,
  }

  if (options?.mode === 'queue' && state.current) {
    const lastQueued = state.queue[state.queue.length - 1]
    if (sameNotification(state.current, payload) || sameNotification(lastQueued, payload)) return
    state.queue.push(payload)
    return
  }

  if (sameNotification(state.current, payload)) {
    scheduleDismiss(payload.duration)
    return
  }

  showNow(payload)
}

const notification = computed(() => state.current)

export const useNotification = () => ({
  notification: readonly(notification),
  showNotification,
  hideNotification: clearNotification,
  clearNotificationQueue: () => {
    state.queue.length = 0
  },
})
