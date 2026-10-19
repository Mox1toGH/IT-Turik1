import { computed, onBeforeUnmount, onMounted, ref, toValue, type MaybeRefOrGetter } from 'vue'
import {
  useGetTournamentLeaderboard,
  type GetTournamentLeaderboardQueryResult,
} from '@/api/evaluation/evaluation'
import { useListRounds } from '@/api/tournaments/tournaments'
import { customInstance } from '@/lib/apiClient'
import { queryClient } from '@/lib/queryClient'
import { subscribeTournamentLeaderboard } from '@/lib/leaderboardSocket'
import { useNotification } from '@/composables/useNotification'
import { getErrorCode } from '@/composables/useQueryState'

export interface LeaderboardRoundColumn {
  id: number
  name: string
  maxScore: number
}

export type LeaderboardTournamentEntry = GetTournamentLeaderboardQueryResult['rankings'][number]
export type LeaderboardRoundBreakdown = NonNullable<LeaderboardTournamentEntry['rounds']>[number]

interface ParsedApiError {
  message?: string
}

function parseApiError(error: unknown): ParsedApiError | null {
  if (!error || typeof error !== 'object') return null
  const withMessage = error as { message?: unknown }
  if (typeof withMessage.message === 'string') return { message: withMessage.message }
  return null
}

function getHttpStatus(error: unknown): number | null {
  if (!error || typeof error !== 'object') return null
  const maybeAxios = error as {
    _axiosError?: { response?: { status?: number } }
    status?: number
  }
  return maybeAxios._axiosError?.response?.status ?? maybeAxios.status ?? null
}

export function getRoundBreakdown(
  entry: LeaderboardTournamentEntry,
  roundId: number,
): LeaderboardRoundBreakdown | null {
  return entry.rounds?.find((item) => item.round_id === roundId) ?? null
}

export function getJuryCount(
  juryBreakdown: unknown,
  totalScore?: number,
  averageScore?: number,
  roundMaxScore?: number,
): number {
  if (Array.isArray(juryBreakdown)) return juryBreakdown.length || 1
  if (juryBreakdown && typeof juryBreakdown === 'object') {
    const count = Object.keys(juryBreakdown as Record<string, unknown>).length
    return count || 1
  }
  if (
    roundMaxScore &&
    roundMaxScore > 0 &&
    averageScore &&
    averageScore > 0 &&
    totalScore !== undefined
  ) {
    const estimated = totalScore / (roundMaxScore * averageScore)
    if (Number.isFinite(estimated) && estimated > 0) return Math.max(1, Math.round(estimated))
  }
  return 1
}

export function formatScore(value: number): string {
  if (Number.isNaN(value)) return '0'
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value)
}

export function useLeaderboard(tournamentId: MaybeRefOrGetter<number>) {
  const tableWrapRef = ref<HTMLElement | null>(null)
  const isCreatingGoogleSheet = ref<boolean>(false)
  const { showNotification } = useNotification()
  let unsubscribeLeaderboardSocket: (() => void) | null = null

  const id = computed<number>(() => toValue(tournamentId))

  const { data: roundsData } = useListRounds(id)
  const rounds = computed(() => roundsData.value?.items ?? [])

  const {
    data: leaderboard,
    isLoading,
    isError,
    isFetching,
    error,
    refetch,
  } = useGetTournamentLeaderboard(id, {
    query: {
      retry: (failureCount: number, queryError: unknown): boolean => {
        const status = getHttpStatus(queryError)
        if (status === 404 || status === 403) return false
        return failureCount < 2
      },
    },
  })

  const rankings = computed<LeaderboardTournamentEntry[]>(() => leaderboard.value?.rankings ?? [])

  const leaderboardRoundIds = computed<Set<number>>(() => {
    const ids = new Set<number>()
    for (const entry of rankings.value)
      for (const round of entry.rounds ?? []) ids.add(round.round_id)
    return ids
  })

  const roundMaxScoreMap = computed<Map<number, number>>(() => {
    const scoreMap = new Map<number, number>()
    for (const round of rounds.value) {
      const criteria = Array.isArray(round.criteria) ? round.criteria : []
      const maxScore = criteria.reduce(
        (sum: number, criterion) => sum + Number(criterion.max_score || 0),
        0,
      )
      scoreMap.set(round.id, maxScore)
    }
    return scoreMap
  })

  const roundColumns = computed<LeaderboardRoundColumn[]>(() => {
    const idsFromLeaderboard = leaderboardRoundIds.value
    const shouldFilterByLeaderboard = idsFromLeaderboard.size > 0
    const baseRounds = shouldFilterByLeaderboard
      ? rounds.value.filter((round) => idsFromLeaderboard.has(round.id))
      : rounds.value
    const columnsFromRounds: LeaderboardRoundColumn[] = baseRounds.map((round) => ({
      id: round.id,
      name: round.name ?? '-',
      maxScore: roundMaxScoreMap.value.get(round.id) ?? 0,
    }))
    if (!shouldFilterByLeaderboard) return columnsFromRounds
    const existingIds = new Set(columnsFromRounds.map((round) => round.id))
    const fallbackColumns: LeaderboardRoundColumn[] = []
    for (const entry of rankings.value) {
      for (const round of entry.rounds ?? []) {
        if (existingIds.has(round.round_id)) continue
        fallbackColumns.push({
          id: round.round_id,
          name: round.round_name,
          maxScore: roundMaxScoreMap.value.get(round.round_id) ?? 0,
        })
        existingIds.add(round.round_id)
      }
    }
    return [...columnsFromRounds, ...fallbackColumns]
  })

  const hasRoundOverflow = computed<boolean>(() => roundColumns.value.length > 3)
  const visibleRoundCols = computed<number>(() => Math.min(roundColumns.value.length, 3))
  const tableVars = computed<Record<string, string>>(() => ({
    '--round-cols': String(Math.max(roundColumns.value.length, 1)),
    '--visible-round-cols': String(Math.max(visibleRoundCols.value, 1)),
  }))

  const errorCode = computed(() => getErrorCode(error.value))

  const isLeaderboardNotReady = computed<boolean>(() => {
    const status = getHttpStatus(error.value)
    return status === 404 || status === 403
  })

  const isExportDisabled = computed<boolean>(
    () => isLoading.value || isError.value || rankings.value.length === 0,
  )

  onMounted(() => {
    unsubscribeLeaderboardSocket = subscribeTournamentLeaderboard(queryClient, id.value)
  })

  onBeforeUnmount(() => {
    unsubscribeLeaderboardSocket?.()
    unsubscribeLeaderboardSocket = null
  })

  function getRoundScore(entry: LeaderboardTournamentEntry, roundId: number): number | null {
    const round = getRoundBreakdown(entry, roundId)
    return round ? round.total_score : null
  }

  function hasRoundParticipation(entry: LeaderboardTournamentEntry, roundId: number): boolean {
    return !!getRoundBreakdown(entry, roundId)
  }

  function getRoundMaxScore(entry: LeaderboardTournamentEntry, roundId: number): number | null {
    const round = getRoundBreakdown(entry, roundId)
    if (!round) return null
    const roundMaxScore = roundMaxScoreMap.value.get(round.round_id) ?? 0
    const juryCount = getJuryCount(
      round.jury_breakdown,
      round.total_score,
      round.average_score,
      roundMaxScore,
    )
    return roundMaxScore * juryCount
  }

  function getEntryMaxScore(entry: LeaderboardTournamentEntry): number {
    return (entry.rounds ?? []).reduce((sum, round) => {
      const roundMaxScore = roundMaxScoreMap.value.get(round.round_id) ?? 0
      const juryCount = getJuryCount(
        round.jury_breakdown,
        round.total_score,
        round.average_score,
        roundMaxScore,
      )
      return sum + roundMaxScore * juryCount
    }, 0)
  }

  function onTableWheel(event: WheelEvent): void {
    const container = tableWrapRef.value
    if (!container || !hasRoundOverflow.value) return
    const maxScrollLeft = container.scrollWidth - container.clientWidth
    if (maxScrollLeft <= 0) return
    const dominantDelta =
      Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY
    if (!dominantDelta) return
    const slowedDelta = dominantDelta * 0.4
    const nextScrollLeft = Math.min(maxScrollLeft, Math.max(0, container.scrollLeft + slowedDelta))
    if (nextScrollLeft !== container.scrollLeft) {
      event.preventDefault()
      container.scrollLeft = nextScrollLeft
    }
  }

  function buildLeaderboardTableRows(): string[][] {
    const header = ['Place', 'Team', ...roundColumns.value.map((round) => round.name), 'Total']
    const rows = rankings.value.map((entry) => {
      const roundValues = roundColumns.value.map((round) =>
        !hasRoundParticipation(entry, round.id)
          ? 'x'
          : `${formatScore(getRoundScore(entry, round.id) ?? 0)}/${formatScore(getRoundMaxScore(entry, round.id) ?? 0)}`,
      )
      return [
        String(entry.rank),
        entry.team_name,
        ...roundValues,
        `${formatScore(entry.total_score)}/${formatScore(getEntryMaxScore(entry))}`,
      ]
    })
    return [header, ...rows]
  }

  function escapeCsvValue(value: string): string {
    return /[",\n]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value
  }

  function handleDownloadCsv(): void {
    if (isExportDisabled.value) {
      showNotification('Leaderboard data is not available yet.', 'error')
      return
    }
    const rows = buildLeaderboardTableRows()
    const csvContent = rows
      .map((row) => row.map((value) => escapeCsvValue(value)).join(','))
      .join('\n')
    const csvBlob = new Blob([`\uFEFF${csvContent}`], { type: 'text/csv;charset=utf-8;' })
    const csvUrl = window.URL.createObjectURL(csvBlob)
    const link = document.createElement('a')
    link.href = csvUrl
    link.download = `tournament-${id.value}-leaderboard-${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(csvUrl)
  }

  async function handleOpenInGoogleSheets(): Promise<void> {
    if (isExportDisabled.value || isCreatingGoogleSheet.value) return
    isCreatingGoogleSheet.value = true
    try {
      const response = await customInstance<{ spreadsheet_url: string }>({
        url: `http://localhost:8000/api/evaluation/tournaments/${id.value}/leaderboard/export-google-sheet/`,
        method: 'POST',
      })
      showNotification('Google Sheet has been created successfully.')
      window.open(response.spreadsheet_url, '_blank', 'noopener,noreferrer')
    } catch (apiError) {
      const parsedError = parseApiError(apiError)
      showNotification(parsedError?.message || 'Failed to create Google Sheet.', 'error')
    } finally {
      isCreatingGoogleSheet.value = false
    }
  }

  return {
    tableWrapRef,
    isCreatingGoogleSheet,
    rankings,
    roundColumns,
    hasRoundOverflow,
    tableVars,
    isLoading,
    isError,
    isFetching,
    error,
    errorCode,
    refetch,
    isLeaderboardNotReady,
    isExportDisabled,
    getRoundScore,
    hasRoundParticipation,
    getRoundMaxScore,
    getEntryMaxScore,
    formatScore,
    onTableWheel,
    handleDownloadCsv,
    handleOpenInGoogleSheets,
  }
}
