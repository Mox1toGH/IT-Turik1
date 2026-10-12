<template>
  <ui-card
    class="stats-section"
    :status="status"
    :is-fetching="isFetching"
    :is-stale="isStale"
    :error-code="errorCode"
    title="statistics"
    @retry="refetchAll"
  >
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
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { useGetAdminStats, useGetPlayerStats, useGetTeamStats } from '@/api/stats/stats'
import { useCardState } from '@/composables/useCardState'
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

const isStaff = computed(() => !!props.user?.is_staff)
const isTeamRole = computed(() => props.user?.role === 'team')
const firstTeamId = computed(() => props.user?.teams?.[0]?.id ?? 0)

const adminQuery = useGetAdminStats({ query: { enabled: isStaff } })
const playerQuery = useGetPlayerStats({
  query: { enabled: computed(() => !!props.user && !isStaff.value) },
})
const teamQuery = useGetTeamStats(firstTeamId, {
  query: { enabled: computed(() => isTeamRole.value && firstTeamId.value > 0), retry: false },
})

const { data: adminStats } = adminQuery
const { data: playerStats } = playerQuery
const { data: teamStats } = teamQuery

const isPlayerActive = computed(() => !!props.user && !isStaff.value)
const isTeamActive = computed(() => isTeamRole.value && firstTeamId.value > 0)

const cardQuery = computed(() => ({
  isPending:
    (isStaff.value && adminQuery.isPending.value) ||
    (isPlayerActive.value && playerQuery.isPending.value) ||
    (isTeamActive.value && teamQuery.isPending.value),
  // Team stats are non-fatal: player stats stay visible if they fail.
  isError:
    (isStaff.value && adminQuery.isError.value) ||
    (isPlayerActive.value && playerQuery.isError.value),
  data:
    (isStaff.value ? adminStats.value : undefined) ??
    (isPlayerActive.value ? playerStats.value : undefined),
  error: adminQuery.error.value ?? playerQuery.error.value ?? null,
}))
const { status, errorCode, isStale } = useCardState(cardQuery)

const isLoading = computed(
  () =>
    (isStaff.value && adminQuery.isPending.value) ||
    (isPlayerActive.value && playerQuery.isPending.value) ||
    (isTeamActive.value && teamQuery.isPending.value),
)
const isFetching = computed(
  () => adminQuery.isFetching.value || playerQuery.isFetching.value || teamQuery.isFetching.value,
)
const refetchAll = () => {
  void adminQuery.refetch()
  void playerQuery.refetch()
  void teamQuery.refetch()
}

const queryError = computed(() => adminQuery.error.value ?? playerQuery.error.value)
const errorMessage = computed(
  () => queryError.value?.message ?? 'Failed to load statistics. Please try again.',
)

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
