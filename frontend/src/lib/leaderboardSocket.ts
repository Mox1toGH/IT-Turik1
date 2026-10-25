import type { QueryClient } from '@tanstack/vue-query'
import { getGetTournamentLeaderboardQueryKey } from '@/api/evaluation/evaluation'

type LeaderboardEnvelope = {
  event: string
  payload?: {
    tournament_id?: number
  }
}

let socket: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let reconnectAttempts = 0
let manuallyClosed = false
let queryClientRef: QueryClient | null = null
let sessionAuthenticated = false
const subscribedTournamentCounts = new Map<number, number>()

const MAX_BACKOFF_MS = 30000

function getWsUrl(): string {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const backend = new URL(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')
  return `${wsProtocol}//${backend.host}/ws/leaderboards/`
}

function clearReconnectTimer() {
  if (!reconnectTimer) return
  clearTimeout(reconnectTimer)
  reconnectTimer = null
}

function send(action: 'subscribe' | 'unsubscribe', tournamentId: number) {
  if (!socket || socket.readyState !== WebSocket.OPEN) return
  socket.send(JSON.stringify({ action, tournament_id: tournamentId }))
}

function resubscribeAll() {
  for (const tournamentId of subscribedTournamentCounts.keys()) {
    send('subscribe', tournamentId)
  }
}

function scheduleReconnect() {
  if (manuallyClosed) return
  clearReconnectTimer()
  if (!sessionAuthenticated) return
  reconnectAttempts += 1
  const delay = Math.min(MAX_BACKOFF_MS, Math.max(1000, 1000 * 2 ** (reconnectAttempts - 1)))
  reconnectTimer = setTimeout(() => connectLeaderboardSocket(), delay)
}

function handleMessage(message: LeaderboardEnvelope) {
  if (message.event !== 'leaderboard.updated') return
  const tournamentId = message.payload?.tournament_id
  if (!queryClientRef || typeof tournamentId !== 'number') return
  queryClientRef.invalidateQueries({
    queryKey: getGetTournamentLeaderboardQueryKey(tournamentId),
  })
}

function connectLeaderboardSocket() {
  if (!queryClientRef) return
  if (!sessionAuthenticated) return
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) return

  manuallyClosed = false
  clearReconnectTimer()
  socket = new WebSocket(getWsUrl())

  socket.onopen = () => {
    reconnectAttempts = 0
    resubscribeAll()
  }

  socket.onmessage = (event) => {
    try {
      handleMessage(JSON.parse(event.data) as LeaderboardEnvelope)
    } catch {
      // Ignore malformed messages.
    }
  }

  socket.onclose = (event) => {
    socket = null
    if (event.code === 4401) {
      import('@/lib/apiClient')
        .then(({ AXIOS_INSTANCE }) => AXIOS_INSTANCE.get('/api/accounts/profile'))
        .then(() => {
          if (sessionAuthenticated) connectLeaderboardSocket()
        })
        .catch(() => {})
      return
    }
    scheduleReconnect()
  }

  socket.onerror = () => {
    socket?.close()
  }
}

export function setLeaderboardSocketAuthenticated(authenticated: boolean) {
  sessionAuthenticated = authenticated
  if (authenticated) {
    connectLeaderboardSocket()
    return
  }
  manuallyClosed = true
  clearReconnectTimer()
  if (socket) {
    socket.close()
    socket = null
  }
}

function maybeCloseSocket() {
  if (subscribedTournamentCounts.size > 0) return
  manuallyClosed = true
  clearReconnectTimer()
  if (socket) {
    socket.close()
    socket = null
  }
}

export function subscribeTournamentLeaderboard(queryClient: QueryClient, tournamentId: number): () => void {
  queryClientRef = queryClient
  connectLeaderboardSocket()

  subscribedTournamentCounts.set(tournamentId, (subscribedTournamentCounts.get(tournamentId) ?? 0) + 1)
  send('subscribe', tournamentId)

  return () => {
    const count = subscribedTournamentCounts.get(tournamentId) ?? 0
    if (count <= 1) {
      subscribedTournamentCounts.delete(tournamentId)
      send('unsubscribe', tournamentId)
    } else {
      subscribedTournamentCounts.set(tournamentId, count - 1)
    }
    maybeCloseSocket()
  }
}

