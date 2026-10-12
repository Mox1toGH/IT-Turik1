<template>
  <section class="preview-shell" aria-labelledby="stats-preview-title">
    <div class="preview-head">
      <h2 id="stats-preview-title">Statistics</h2>
    </div>

    <p v-if="isError" class="preview-error">Unable to load stats preview right now.</p>

    <ui-skeleton-loader :loading="isLoading">
      <template #skeleton>
        <div class="preview-grid">
          <ui-skeleton v-for="n in 4" :key="n" variant="rect" height="82px" />
        </div>
      </template>

      <div class="preview-grid">
        <ui-card v-for="item in cards" :key="item.label" class="preview-item">
          <p class="label">{{ item.label }}</p>
          <p class="value">
            <RouterLink v-if="item.to" :to="item.to">{{ item.value }}</RouterLink>
            <span v-else>{{ item.value }}</span>
          </p>
        </ui-card>
      </div>
    </ui-skeleton-loader>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { useGetAdminStats, useGetPlayerStats, useGetTeamStats } from '@/api/stats/stats'
import UiCard from '../ui/UiCard.vue'
import type { UserRole } from '@/api/backendAPINinja.schemas.ts'

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
const isPlayerActive = computed(() => !!props.user && !isStaff.value)
const firstTeamId = computed(() => props.user?.teams?.[0]?.id ?? 0)
const isTeamActive = computed(() => isTeamRole.value && firstTeamId.value > 0)

const adminQuery = useGetAdminStats({ query: { enabled: isStaff } })
const playerQuery = useGetPlayerStats({ query: { enabled: isPlayerActive } })
const teamQuery = useGetTeamStats(firstTeamId, {
  query: { enabled: isTeamActive, retry: false },
})

const { data: adminStats } = adminQuery
const { data: playerStats } = playerQuery
const { data: teamStats } = teamQuery

const isLoading = computed(
  () =>
    (isStaff.value && adminQuery.isPending.value) ||
    (isPlayerActive.value && playerQuery.isPending.value) ||
    (isTeamActive.value && teamQuery.isPending.value),
)
// Team stats are non-fatal: player stats stay visible if they fail.
const isError = computed(
  () =>
    (isStaff.value && adminQuery.isError.value) ||
    (isPlayerActive.value && playerQuery.isError.value),
)

const cards = computed(() => {
  if (props.user?.is_staff) {
    return [
      { label: 'Total users', value: String(adminStats.value?.total_users ?? 0), to: undefined },
      {
        label: 'Total tournaments',
        value: String(adminStats.value?.total_tournaments ?? 0),
        to: undefined,
      },
      {
        label: 'Active tournaments',
        value: String(adminStats.value?.active_tournaments ?? 0),
        to: undefined,
      },
      {
        label: 'New this week',
        value: String(adminStats.value?.new_registrations_last_7_days ?? 0),
        to: undefined,
      },
    ]
  }

  const currentTeamName = playerStats.value?.current_team_name
  const currentTeam =
    props.user?.teams?.find((team) => team.name === currentTeamName) ?? props.user?.teams?.[0]

  const base = [
    {
      label: 'Win rate',
      value: `${(playerStats.value?.win_rate ?? 0).toFixed(2)}%`,
      to: undefined,
    },
    {
      label: 'Total tournaments',
      value: String(playerStats.value?.total_tournaments ?? 0),
      to: undefined,
    },
    {
      label: 'Average score',
      value: (playerStats.value?.average_evaluation_score ?? 0).toFixed(2),
      to: undefined,
    },
    {
      label: 'Current team',
      value: playerStats.value?.current_team_name || 'No team',
      to: currentTeam ? `/teams/${currentTeam.id}` : undefined,
    },
  ]

  if (props.user?.role === 'team') {
    return [
      ...base,
      {
        label: 'Active members',
        value: String(teamStats.value?.active_members_count ?? 0),
        to: undefined,
      },
    ]
  }

  return base
})
</script>

<style scoped>
.preview-shell {
  display: grid;
  gap: 0.7rem;
}

.preview-head h2 {
  margin: 0;
  font-family: var(--font-display);
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.6rem;
}

.label {
  margin: 0;
  font-size: 0.8rem;
  color: var(--muted-foreground);
}

.value {
  margin: 0.35rem 0 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--foreground);
}

.value-link:hover {
  text-decoration: underline;
}

.preview-error {
  margin: 0;
  color: var(--muted-foreground);
}

@media (max-width: 900px) {
  .preview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
