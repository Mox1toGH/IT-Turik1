<template>
  <ui-card class="stats-section" :query="playerQuery" title="statistics">
    <template #header>
      <h2>Statistics</h2>
    </template>

    <template #error>
      <div class="error-state">
        <p>{{ errorMessage }}</p>
      </div>
    </template>

    <template #skeleton>
      <div class="stats-grid">
        <ui-skeleton v-for="n in 6" :key="n" variant="rect" height="84px" />
      </div>
    </template>

    <div class="stats-grid">
      <ui-card v-for="item in statsCards" :key="item.label" class="stat-card">
        <p class="stat-label">{{ item.label }}</p>
        <p class="stat-value">{{ item.value }}</p>
      </ui-card>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useGetPlayerStats, useGetTeamStats } from '@/api/stats/stats'
import type { UserRole } from '@/api/backendAPINinja.schemas'

type TeamRef = { id: number; name: string }
type ProfileLike = {
  role?: UserRole
  is_staff?: boolean
  readonly teams?: readonly TeamRef[]
}

interface Props {
  user?: ProfileLike | null
}

const props = defineProps<Props>()

const firstTeamId = computed(() => props.user?.teams?.[0]?.id ?? 0)

// Primary query: drives the card's status.
const playerQuery = useGetPlayerStats()
// Secondary query: own loading state, never affects the card's status.
const teamQuery = useGetTeamStats(firstTeamId, {
  query: {
    enabled: computed(() => props.user?.role === 'team' && firstTeamId.value > 0),
    retry: false,
  },
})

const { data: playerStats } = playerQuery
const { data: teamStats } = teamQuery

const errorMessage = computed(
  () => playerQuery.error.value?.message ?? 'Failed to load statistics. Please try again.',
)

const formatPercent = (value: number | null | undefined) => `${(value ?? 0).toFixed(2)}%`
const formatScore = (value: number | null | undefined) => (value ?? 0).toFixed(2)

const statsCards = computed(() => {
  const cards = [
    { label: 'Total tournaments', value: String(playerStats.value?.total_tournaments ?? 0) },
    {
      label: 'Wins / Losses',
      value: `${playerStats.value?.wins ?? 0} / ${playerStats.value?.losses ?? 0}`,
    },
    { label: 'Win rate', value: formatPercent(playerStats.value?.win_rate) },
    {
      label: 'Average evaluation score',
      value: formatScore(playerStats.value?.average_evaluation_score),
    },
    { label: 'Current team', value: playerStats.value?.current_team_name || 'No team' },
  ]

  if (props.user?.role === 'team') {
    cards.push(
      { label: 'Team win rate', value: formatPercent(teamStats.value?.win_rate) },
      { label: 'Active team members', value: String(teamStats.value?.active_members_count ?? 0) },
      {
        label: 'Top player',
        value: teamStats.value?.top_player
          ? `${teamStats.value.top_player.username} (${formatScore(
              teamStats.value.top_player.average_evaluation_score,
            )})`
          : 'No data',
      },
    )
  }

  return cards
})
</script>

<style scoped>
.stats-section h2 {
  margin-top: 0;
  font-family: var(--font-display);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.stat-card {
  gap: 0.35rem;
}

.stat-label {
  margin: 0;
  color: var(--muted-foreground);
  font-size: 0.82rem;
}

.stat-value {
  margin: 0;
  font-size: 1.08rem;
  font-weight: 700;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.error-state {
  min-height: 110px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--muted-foreground);
}

@media (max-width: 980px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
