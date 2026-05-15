import type { QueryClient } from '@tanstack/vue-query'

import type { Notification, PaginatedNotificationList } from '@/api/.ts.schemas'
import {
  getGetUnreadNotificationCountQueryKey,
  getListNotificationsQueryKey,
} from '@/api/notifications/notifications'

type SocketEnvelope = {
  event: string
  payload: Record<string, unknown>
}

let socket: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let manuallyClosed = false
let reconnectAttempts = 0
let clientRef: QueryClient | null = null

const MAX_BACKOFF_MS = 30000

const unreadKey = getGetUnreadNotificationCountQueryKey()

function listQueryPrefix() {
  return getListNotificationsQueryKey().slice(0, 4)
}

function getWsUrl(token: string): string {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.hostname
  const port = '8000'
  return `${wsProtocol}//${host}:${port}/ws/notifications/?token=${encodeURIComponent(token)}`
}

function applyUnreadCount(unreadCount: number) {
  if (!clientRef) return
  clientRef.setQueryData(unreadKey, { unread_count: unreadCount })
}

function applyNotificationCreated(notification: Notification) {
  if (!clientRef) return
  clientRef.setQueriesData({ queryKey: listQueryPrefix(), exact: false }, (old) => {
    const current = old as PaginatedNotificationList | undefined
    if (!current?.results) return old
    if (current.results.some((n) => n.id === notification.id)) return current
    return {
      ...current,
      count: (current.count ?? current.results.length) + 1,
      results: [notification, ...current.results],
    }
  })
}

function applyReadStatusChanged(ids: number[], isRead: boolean) {
  if (!clientRef) return
  const idSet = new Set(ids)
  clientRef.setQueriesData({ queryKey: listQueryPrefix(), exact: false }, (old) => {
    const current = old as PaginatedNotificationList | undefined
    if (!current?.results) return old
    return {
      ...current,
      results: current.results.map((item) =>
        idSet.has(item.id) ? { ...item, is_read: isRead } : item,
      ),
    }
  })
}

function applyDeleted(ids: number[]) {
  if (!clientRef) return
  const idSet = new Set(ids)
  clientRef.setQueriesData({ queryKey: listQueryPrefix(), exact: false }, (old) => {
    const current = old as PaginatedNotificationList | undefined
    if (!current?.results) return old
    const filtered = current.results.filter((item) => !idSet.has(item.id))
    return {
      ...current,
      count: Math.max(0, (current.count ?? current.results.length) - (current.results.length - filtered.length)),
      results: filtered,
    }
  })
}

function handleMessage(data: SocketEnvelope) {
  const payload = data.payload ?? {}
  if (data.event === 'notification.created') {
    const notification = payload.notification as Notification | undefined
    if (notification) applyNotificationCreated(notification)
    return
  }
  if (data.event === 'notification.unread_count_updated') {
    const unreadCount = payload.unread_count as number | undefined
    if (typeof unreadCount === 'number') applyUnreadCount(unreadCount)
    return
  }
  if (data.event === 'notification.read_status_changed') {
    const ids = (payload.notification_ids as number[] | undefined) ?? []
    const isRead = payload.is_read as boolean | undefined
    if (Array.isArray(ids) && typeof isRead === 'boolean') applyReadStatusChanged(ids, isRead)
    return
  }
  if (data.event === 'notification.deleted') {
    const ids = (payload.notification_ids as number[] | undefined) ?? []
    if (Array.isArray(ids)) applyDeleted(ids)
  }
}

function clearReconnectTimer() {
  if (!reconnectTimer) return
  clearTimeout(reconnectTimer)
  reconnectTimer = null
}

function scheduleReconnect() {
  if (manuallyClosed) return
  clearReconnectTimer()
  const token = localStorage.getItem('access')
  if (!token) return
  reconnectAttempts += 1
  const delay = Math.min(MAX_BACKOFF_MS, Math.max(1000, 1000 * 2 ** (reconnectAttempts - 1)))
  reconnectTimer = setTimeout(() => {
    connectNotificationSocket()
  }, delay)
}

export function connectNotificationSocket(queryClient?: QueryClient) {
  if (queryClient) clientRef = queryClient
  if (!clientRef) return

  const token = localStorage.getItem('access')
  if (!token) return

  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
    return
  }

  manuallyClosed = false
  clearReconnectTimer()
  socket = new WebSocket(getWsUrl(token))

  socket.onopen = () => {
    reconnectAttempts = 0
  }

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as SocketEnvelope
      handleMessage(data)
    } catch {
      clientRef?.invalidateQueries({ queryKey: listQueryPrefix(), exact: false })
      clientRef?.invalidateQueries({ queryKey: unreadKey })
    }
  }

  socket.onclose = () => {
    socket = null
    scheduleReconnect()
  }

  socket.onerror = () => {
    socket?.close()
  }
}

export function disconnectNotificationSocket() {
  manuallyClosed = true
  clearReconnectTimer()
  if (socket) {
    socket.close()
    socket = null
  }
}
