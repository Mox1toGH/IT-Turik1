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
          <div class="leaderboard-table-wrap">
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
                  <td v-for="round in roundColumns" :key="`${entry.team_id}-${round.id}`" class="round-cell">
                    <template v-if="hasRoundParticipation(entry, round.id)">
                      {{ formatScore(getRoundScore(entry, round.id) ?? 0) }}
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
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { parseApiError } from '@/api/errors'
import { useTournamentRounds } from '@/api/queries/tournaments'
import { useTournamentLeaderboard } from '@/api/queries/evaluation'
import type { GetTournamentLeaderboardResponse } from '@/api/services/evaluation/types'

interface Props {
  tournamentId: number
}

interface RoundColumn {
  id: number
  name: string
  maxScore: number
}

type TournamentEntry = GetTournamentLeaderboardResponse['rankings'][number]

const props = defineProps<Props>()

const {
  data: roundsData,
} = useTournamentRounds({ id: props.tournamentId })
const rounds = computed(() => roundsData.value ?? [])

const tournamentQuery = useTournamentLeaderboard({ tournamentId: props.tournamentId })
const isLoading = computed(() => tournamentQuery.isLoading.value)
const isError = computed(() => tournamentQuery.isError.value)
const error = computed(() => parseApiError(tournamentQuery.error.value))
const rankings = computed<TournamentEntry[]>(() => tournamentQuery.data.value?.rankings ?? [])

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
    name: round.name,
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

const tableVars = computed(() => ({
  '--round-cols': String(Math.max(roundColumns.value.length, 1)),
}))

const errorMessage = computed(() => {
  if (!error.value) return 'Failed to load leaderboard.'
  if (error.value.code === 'forbidden') return 'Leaderboard is not available yet.'
  return error.value.message || 'Failed to load leaderboard.'
})

function getRoundScore(entry: TournamentEntry, roundId: number) {
  const round = entry.rounds?.find((item) => item.round_id === roundId)
  return round ? round.total_score : null
}

function hasRoundParticipation(entry: TournamentEntry, roundId: number) {
  return getRoundScore(entry, roundId) !== null
}

function getEntryMaxScore(entry: TournamentEntry) {
  return (entry.rounds ?? []).reduce((sum, round) => {
    const roundMaxScore = roundMaxScoreMap.value.get(round.round_id) ?? 0
    const juryCount = getJuryCount(round.jury_breakdown)
    return sum + roundMaxScore * juryCount
  }, 0)
}

function getJuryCount(juryBreakdown: unknown) {
  if (Array.isArray(juryBreakdown)) return juryBreakdown.length || 1
  if (juryBreakdown && typeof juryBreakdown === 'object') {
    const count = Object.keys(juryBreakdown as Record<string, unknown>).length
    return count || 1
  }
  return 1
}

function formatScore(value: number) {
  if (Number.isNaN(value)) return '0'
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value)
}
</script>

<style scoped>
.leaderboard-shell {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--card);
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
  z-index: 4;
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
  z-index: 3;
  background: var(--card);
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
