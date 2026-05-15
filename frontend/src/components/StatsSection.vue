<template>
  <ui-card class="stats-section" :is-error="isError">
    <template #header>
      <h2>Statistics</h2>
    </template>

    <template #error>
      <div class="error-state">
        <p>{{ errorMessage }}</p>
      </div>
    </template>

    <ui-skeleton-loader :loading="isLoading">
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
    </ui-skeleton-loader>
  </ui-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import type { RoleB96Enum } from '@/api/.ts.schemas'
import { getAdminStats, getPlayerStats, getTeamStats } from '@/api/stats/stats'

type UserRole = RoleB96Enum
type TeamRef = { id: number; name: string }
type ProfileLike = {
  role?: UserRole
  is_staff?: boolean
  readonly teams?: readonly TeamRef[]
}

type PlayerStatsResponse = {
  total_tournaments: number
  wins: number
  losses: number
  win_rate: number
  average_evaluation_score: number
  current_team_name: string | null
}

type TeamStatsResponse = {
  win_rate: number
  active_members_count: number
  top_player: {
    username: string
    average_evaluation_score: number
  } | null
}

type AdminStatsResponse = {
  total_users: number
  total_teams: number
  total_tournaments: number
  new_registrations_last_7_days: number
  new_registrations_last_30_days: number
  active_tournaments: number
  users_by_role: Array<{ role: string; count: number }>
}

interface Props {
  user?: ProfileLike | null
}

const props = defineProps<Props>()

const isLoading = ref(false)
const isError = ref(false)
const errorMessage = ref('Failed to load statistics. Please try again.')

const playerStats = ref<PlayerStatsResponse | null>(null)
const teamStats = ref<TeamStatsResponse | null>(null)
const adminStats = ref<AdminStatsResponse | null>(null)

const formatPercent = (value: number | null | undefined) => `${(value ?? 0).toFixed(2)}%`
const formatScore = (value: number | null | undefined) => (value ?? 0).toFixed(2)

const roleBreakdown = computed(() => {
  const breakdown = adminStats.value?.users_by_role ?? []
  if (breakdown.length === 0) return 'No data'
  return breakdown.map((item) => `${item.role}: ${item.count}`).join(', ')
})

const statsCards = computed(() => {
  if (props.user?.is_staff) {
    return [
      { label: 'Total users', value: String(adminStats.value?.total_users ?? 0) },
      { label: 'Total teams', value: String(adminStats.value?.total_teams ?? 0) },
      { label: 'Total tournaments', value: String(adminStats.value?.total_tournaments ?? 0) },
      {
        label: 'New registrations (7d / 30d)',
        value: `${adminStats.value?.new_registrations_last_7_days ?? 0} / ${
          adminStats.value?.new_registrations_last_30_days ?? 0
        }`,
      },
      { label: 'Active tournaments', value: String(adminStats.value?.active_tournaments ?? 0) },
      { label: 'Role breakdown', value: roleBreakdown.value },
    ]
  }

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

const loadStats = async () => {
  if (!props.user) return

  isLoading.value = true
  isError.value = false
  errorMessage.value = 'Failed to load statistics. Please try again.'
  playerStats.value = null
  teamStats.value = null
  adminStats.value = null

  try {
    if (props.user.is_staff) {
      const data = await getAdminStats()
      adminStats.value = data
      return
    }

    const data = await getPlayerStats()
    playerStats.value = data

    if (props.user.role === 'team') {
      const firstTeamId = props.user.teams?.[0]?.id
      if (!firstTeamId) return

      try {
        const data = await getTeamStats(firstTeamId)
        teamStats.value = data
      } catch {
        // Keep player stats visible if team stats are unavailable for this user/team.
      }
    }
  } catch (error) {
    isError.value = true

    if (error instanceof Error) {
      errorMessage.value = error.message
    } else if (typeof error === 'string') {
      errorMessage.value = error
    } else {
      errorMessage.value = 'An unknown error occurred.'
    }
  } finally {
    isLoading.value = false
  }
}

watch(
  () => props.user,
  () => {
    if (props.user) void loadStats()
  },
  { deep: true },
)

onMounted(() => {
  if (props.user) void loadStats()
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
