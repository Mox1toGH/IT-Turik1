<template>
  <section class="leaderboard-shell">
    <ui-card>
      <template #header>
        <div class="header">
          <div>
            <h3>Leaderboard</h3>
            <p class="text-muted">Scores and rankings for this tournament.</p>
          </div>

          <div class="controls">
            <ui-badge variant="green">Snapshot</ui-badge>
          </div>
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div class="table-skeleton">
            <ui-skeleton variant="rect" height="40px" />
            <ui-skeleton v-for="i in 5" :key="i" variant="rect" height="52px" />
          </div>
        </template>

        <ui-card v-if="isError" class="empty">
          <p>{{ errorMessage }}</p>
        </ui-card>

        <ui-card v-else-if="rankings.length === 0" class="empty">
          <p>No leaderboard data yet.</p>
        </ui-card>

        <template v-else>
          <div
            ref="tableWrapRef"
            class="leaderboard-table-wrap"
            :class="{ 'is-rounds-scroll-capped': hasRoundOverflow }"
            @wheel="onTableWheel"
          >
            <table class="leaderboard-table" :style="tableVars">
              <thead>
                <tr>
                  <th class="rank-col sticky-left">Place</th>
                  <th class="team-col sticky-left">Team</th>
                  <th v-for="round in roundColumns" :key="round.id" class="round-col">
                    {{ round.name }}
                  </th>
                  <th class="total-col sticky-right">Total</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="entry in rankings" :key="entry.team_id">
                  <td class="rank-col sticky-left">{{ entry.rank }}</td>
                  <td class="team-col sticky-left">
                    <RouterLink :to="`/teams/${entry.team_id}`" class="team-link">
                      {{ entry.team_name }}
                    </RouterLink>
                  </td>
                  <td
                    v-for="round in roundColumns"
                    :key="`${entry.team_id}-${round.id}`"
                    class="round-cell"
                  >
                    <template v-if="hasRoundParticipation(entry, round.id)">
                      {{ formatScore(getRoundScore(entry, round.id) ?? 0) }}/{{
                        formatScore(getRoundMaxScore(entry, round.id) ?? 0)
                      }}
                    </template>
                    <span v-else class="missed-round">x</span>
                  </td>
                  <td class="total-col sticky-right total-value">
                    {{ formatScore(entry.total_score) }}/{{ formatScore(getEntryMaxScore(entry)) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <p v-if="hasRoundOverflow" class="scroll-hint text-muted">
            Scroll horizontally to view all rounds.
          </p>
        </template>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { useListRounds } from '@/api/tournaments/tournaments'
import {
  useGetTournamentLeaderboard,
  type GetTournamentLeaderboardQueryResult,
} from '@/api/evaluation/evaluation'

interface Props {
  tournamentId: number
}

interface RoundColumn {
  id: number
  name: string
  maxScore: number
}

type TournamentEntry = GetTournamentLeaderboardQueryResult['rankings'][number]

const props = defineProps<Props>()
const tableWrapRef = ref<HTMLElement | null>(null)

const { data: roundsData } = useListRounds(props.tournamentId)
const rounds = computed(() => roundsData.value ?? [])

const {
  data: leaderboard,
  isLoading,
  isError,
  error,
} = useGetTournamentLeaderboard(props.tournamentId)
const rankings = computed<TournamentEntry[]>(() => leaderboard.value?.rankings ?? [])

const leaderboardRoundIds = computed(() => {
  const ids = new Set<number>()
  for (const entry of rankings.value) {
    for (const round of entry.rounds ?? []) {
      ids.add(round.round_id)
    }
  }

  return ids
})

const roundMaxScoreMap = computed(() => {
  const scoreMap = new Map<number, number>()

  for (const round of rounds.value) {
    const criteria = Array.isArray(round.criteria) ? round.criteria : []
    const maxScore = criteria.reduce((sum, criterion) => sum + Number(criterion.max_score || 0), 0)
    scoreMap.set(round.id, maxScore)
  }

  return scoreMap
})

const roundColumns = computed<RoundColumn[]>(() => {
  const idsFromLeaderboard = leaderboardRoundIds.value
  const shouldFilterByLeaderboard = idsFromLeaderboard.size > 0

  const baseRounds = shouldFilterByLeaderboard
    ? rounds.value.filter((round) => idsFromLeaderboard.has(round.id))
    : rounds.value

  const columnsFromRounds: RoundColumn[] = baseRounds.map((round) => ({
    id: round.id,
    name: round.name ?? '-',
    maxScore: roundMaxScoreMap.value.get(round.id) ?? 0,
  }))

  if (!shouldFilterByLeaderboard) return columnsFromRounds

  const existingIds = new Set(columnsFromRounds.map((round) => round.id))
  const fallbackColumns: RoundColumn[] = []

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

const hasRoundOverflow = computed(() => roundColumns.value.length > 3)
const visibleRoundCols = computed(() => Math.min(roundColumns.value.length, 3))

const tableVars = computed(() => ({
  '--round-cols': String(Math.max(roundColumns.value.length, 1)),
  '--visible-round-cols': String(Math.max(visibleRoundCols.value, 1)),
}))

const errorMessage = computed(() => {
  if (!error.value) return 'Failed to load leaderboard.'
  if (error.value.code === 'forbidden') return 'Leaderboard is not available yet.'
  return error.value.message || 'Failed to load leaderboard.'
})

function getRoundScore(entry: TournamentEntry, roundId: number) {
  const round = getRoundBreakdown(entry, roundId)
  return round ? round.total_score : null
}

function hasRoundParticipation(entry: TournamentEntry, roundId: number) {
  return !!getRoundBreakdown(entry, roundId)
}

function getRoundMaxScore(entry: TournamentEntry, roundId: number) {
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

function getEntryMaxScore(entry: TournamentEntry) {
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

function getRoundBreakdown(entry: TournamentEntry, roundId: number) {
  return entry.rounds?.find((item) => item.round_id === roundId) ?? null
}

function getJuryCount(
  juryBreakdown: unknown,
  totalScore?: number,
  averageScore?: number,
  roundMaxScore?: number,
) {
  if (Array.isArray(juryBreakdown)) return juryBreakdown.length || 1
  if (juryBreakdown && typeof juryBreakdown === 'object') {
    const count = Object.keys(juryBreakdown as Record<string, unknown>).length
    return count || 1
  }

  // Fallback for hidden jury breakdown (team role): infer from aggregate values per round.
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

function formatScore(value: number) {
  if (Number.isNaN(value)) return '0'
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value)
}

function onTableWheel(event: WheelEvent) {
  const container = tableWrapRef.value
  if (!container || !hasRoundOverflow.value) return

  const maxScrollLeft = container.scrollWidth - container.clientWidth
  if (maxScrollLeft <= 0) return

  const dominantDelta =
    Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY
  if (!dominantDelta) return

  const scrollSpeedFactor = 0.4
  const slowedDelta = dominantDelta * scrollSpeedFactor

  const nextScrollLeft = Math.min(maxScrollLeft, Math.max(0, container.scrollLeft + slowedDelta))

  if (nextScrollLeft !== container.scrollLeft) {
    event.preventDefault()
    container.scrollLeft = nextScrollLeft
  }
}
</script>

<style scoped>
.leaderboard-shell {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.controls {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: end;
  margin-left: auto;
}

.table-skeleton {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.leaderboard-table-wrap {
  position: relative;
  isolation: isolate;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--card);
}

.leaderboard-table-wrap.is-rounds-scroll-capped {
  max-width: min(100%, calc(5.5rem + 15rem + (var(--visible-round-cols) * 7.5rem) + 10rem));
}

.leaderboard-table {
  width: 100%;
  min-width: calc(5.5rem + 15rem + (var(--round-cols) * 7.5rem) + 10rem);
  border-collapse: separate;
  border-spacing: 0;
}

.leaderboard-table th,
.leaderboard-table td {
  padding: 0.75rem 0.8rem;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
  background: var(--card);
}

.leaderboard-table thead th {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  background: color-mix(in srgb, var(--card) 92%, var(--foreground) 8%);
  position: sticky;
  top: 0;
  z-index: 10;
  overflow: hidden;
  text-overflow: ellipsis;
}

.leaderboard-table tbody tr:hover td {
  background: color-mix(in srgb, var(--card) 92%, var(--primary) 8%);
}

.rank-col {
  width: 5.5rem;
  min-width: 5.5rem;
  text-align: center;
  font-weight: 700;
}

.team-col {
  width: 15rem;
  min-width: 15rem;
  max-width: 15rem;
}

.round-col,
.round-cell {
  width: 7.5rem;
  min-width: 7.5rem;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.total-col {
  width: 10rem;
  min-width: 10rem;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.total-value {
  font-weight: 700;
}

.sticky-left,
.sticky-right {
  position: sticky;
  z-index: 5;
  background: var(--card);
}

.leaderboard-table thead .sticky-left,
.leaderboard-table thead .sticky-right {
  z-index: 12;
}

.leaderboard-table thead .rank-col.sticky-left {
  z-index: 13;
}

.rank-col.sticky-left {
  left: 0;
  box-shadow: 1px 0 0 var(--border);
}

.team-col.sticky-left {
  left: 5.5rem;
  box-shadow: 1px 0 0 var(--border);
}

.total-col.sticky-right {
  right: 0;
  box-shadow: -1px 0 0 var(--border);
}

.team-link {
  color: var(--foreground);
  text-decoration: none;
  font-weight: 600;
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

.team-link:hover,
.team-link:focus-visible {
  color: var(--primary);
  text-decoration: underline;
}

.missed-round {
  display: inline-block;
  color: var(--text-muted);
  font-weight: 700;
}

.scroll-hint {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  text-align: right;
}

.empty {
  display: flex;
  height: 220px;
  align-items: center;
  justify-content: center;
}

@media (max-width: 900px) {
  .team-col {
    width: 12rem;
    min-width: 12rem;
    max-width: 12rem;
  }

  .leaderboard-table {
    min-width: calc(5rem + 12rem + (var(--round-cols) * 7rem) + 9rem);
  }

  .leaderboard-table-wrap.is-rounds-scroll-capped {
    max-width: min(100%, calc(5rem + 12rem + (var(--visible-round-cols) * 7rem) + 9rem));
  }

  .rank-col {
    width: 5rem;
    min-width: 5rem;
  }

  .team-col.sticky-left {
    left: 5rem;
  }

  .round-col,
  .round-cell {
    width: 7rem;
    min-width: 7rem;
  }

  .total-col {
    width: 9rem;
    min-width: 9rem;
  }
}
</style>
