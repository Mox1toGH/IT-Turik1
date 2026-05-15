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
const subscribedTournamentCounts = new Map<number, number>()

const MAX_BACKOFF_MS = 30000

function getWsUrl(token: string): string {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.hostname
  const port = '8000'
  return `${wsProtocol}//${host}:${port}/ws/leaderboards/?token=${encodeURIComponent(token)}`
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
  const token = localStorage.getItem('access')
  if (!token) return
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
  const token = localStorage.getItem('access')
  if (!token) return
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) return

  manuallyClosed = false
  clearReconnectTimer()
  socket = new WebSocket(getWsUrl(token))

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

  socket.onclose = () => {
    socket = null
    scheduleReconnect()
  }

  socket.onerror = () => {
    socket?.close()
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

