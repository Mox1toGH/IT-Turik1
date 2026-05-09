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
            <ui-select
              v-model="selectedLeaderboardMode"
              :options="roundOptions"
              :is-loading="isLoadingRounds"
              :is-error="isRoundsError"
              error="Failed to fetch rounds"
              placeholder="Select round"
              align-to="right"
              min-width="200px"
            />
          </div>
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div class="cards">
            <ui-card v-for="i in 3" :key="i" class="entry">
              <template #header>
                <div class="entry-header">
                  <ui-skeleton variant="rect" width="150px" height="22px" />
                  <ui-skeleton variant="rect" width="70px" height="22px" />
                </div>
              </template>

              <div class="entry-body">
                <ui-skeleton variant="rect" width="200px" />
                <ui-skeleton variant="rect" width="230px" />
              </div>
            </ui-card>
          </div>
        </template>

        <ui-card v-if="isError" class="empty">
          <p>{{ errorMessage }}</p>
        </ui-card>

        <ui-card v-else-if="rankings.length === 0" class="empty">
          <p>No leaderboard data yet.</p>
        </ui-card>

        <div v-else class="cards">
          <ui-card v-for="entry in rankings" :key="entry.team_id" class="entry">
            <template #header>
              <div class="entry-header">
                <div class="entry-title">
                  <p class="entry-rank">#{{ entry.rank }}</p>
                  <h4 class="entry-team">{{ entry.team_name }}</h4>
                </div>

                <div class="entry-meta">
                  <ui-badge :variant="isSnapshot ? 'green' : 'gray'">
                    {{ isSnapshot ? 'Snapshot' : 'Live' }}
                  </ui-badge>
                  <p class="entry-score">{{ formatScore(entry.total_score) }}</p>
                </div>
              </div>
            </template>

            <div class="entry-body">
              <template v-if="isAverageMode">
                <div class="rounds" v-if="(entry as TournamentEntry).rounds?.length">
                  <div
                    class="round-row"
                    v-for="round in (entry as TournamentEntry).rounds"
                    :key="round.round_id"
                  >
                    <div class="round-left">
                      <p class="round-name">{{ round.round_name }}</p>
                      <p class="text-muted">Avg: {{ formatScore(round.average_score) }}</p>
                    </div>

                    <div class="round-right">
                      <p class="round-score">{{ formatScore(round.total_score) }}</p>
                    </div>
                  </div>
                </div>
              </template>

              <template v-else>
                <p class="text-muted">
                  Avg: {{ formatScore((entry as RoundEntry).average_score) }}
                </p>
              </template>
            </div>
          </ui-card>
        </div>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { parseApiError } from '@/api/errors'
import { useTournamentRounds } from '@/api/queries/tournaments'
import { useRoundLeaderboard, useTournamentLeaderboard } from '@/api/queries/evaluation'
import type {
  GetRoundLeaderboardResponse,
  GetTournamentLeaderboardResponse,
} from '@/api/services/evaluation/types'

interface Props {
  tournamentId: number
}

type RoundEntry = GetRoundLeaderboardResponse['rankings'][number]
type TournamentEntry = GetTournamentLeaderboardResponse['rankings'][number]

const props = defineProps<Props>()

type LeaderboardMode = 'average' | number
const selectedLeaderboardMode = ref<LeaderboardMode>('average')

const {
  data: roundsData,
  isLoading: isLoadingRounds,
  isError: isRoundsError,
} = useTournamentRounds({ id: props.tournamentId })
const rounds = computed(() => roundsData.value ?? [])

const roundOptions = computed(() => {
  const options: { label: string; value: string | number }[] = [
    { label: 'Average', value: 'average' },
  ]
  options.push(...rounds.value.map((round) => ({ label: round.name, value: round.id })))
  return options
})

const isAverageMode = computed(() => selectedLeaderboardMode.value === 'average')
const selectedRoundId = computed(() =>
  typeof selectedLeaderboardMode.value === 'number' ? selectedLeaderboardMode.value : null,
)

const tournamentQuery = useTournamentLeaderboard(
  { tournamentId: props.tournamentId },
  { enabled: isAverageMode },
)

const roundQuery = useRoundLeaderboard(
  { roundId: computed(() => selectedRoundId.value ?? 0) },
  { enabled: computed(() => !isAverageMode.value && !!selectedRoundId.value) },
)

const activeQuery = computed(() => (isAverageMode.value ? tournamentQuery : roundQuery))

const isLoading = computed(() => activeQuery.value.isLoading.value)
const isError = computed(() => activeQuery.value.isError.value)
const error = computed(() => parseApiError(activeQuery.value.error.value))

const isSnapshot = computed(() =>
  isAverageMode.value
    ? !!tournamentQuery.data.value?.is_snapshot
    : !!roundQuery.data.value?.is_snapshot,
)

const rankings = computed<(RoundEntry | TournamentEntry)[]>(() => {
  if (isAverageMode.value) return (tournamentQuery.data.value?.rankings ?? []) as TournamentEntry[]
  return (roundQuery.data.value?.rankings ?? []) as RoundEntry[]
})

const errorMessage = computed(() => {
  if (!error.value) return 'Failed to load leaderboard.'
  if (error.value.code === 'forbidden') return 'Leaderboard is not available yet.'
  return error.value.message || 'Failed to load leaderboard.'
})

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

.cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.entry {
  min-width: 0;
}

.entry-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}

.entry-title {
  display: flex;
  gap: 0.6rem;
  align-items: baseline;
  min-width: 0;
}

.entry-rank {
  font-weight: 700;
  color: var(--foreground);
  flex-shrink: 0;
}

.entry-team {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.entry-meta {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}

.entry-score {
  font-weight: 700;
}

.entry-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.rounds {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.round-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--input);
}

.round-left {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.round-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.round-right {
  flex-shrink: 0;
}

.round-score {
  font-weight: 700;
}

.empty {
  display: flex;
  height: 220px;
  align-items: center;
  justify-content: center;
}

@media (max-width: 900px) {
  .cards {
    grid-template-columns: 1fr;
  }
}
</style>
