<template>
  <ui-card class="preview-shell" :is-error="isError">
    <template #header>
      <div class="preview-head">
        <h2>Statistics</h2>
      </div>
    </template>

    <template #error>
      <p class="preview-error">Unable to load stats preview right now.</p>
    </template>

    <ui-skeleton-loader :loading="isLoading">
      <template #skeleton>
        <div class="preview-grid">
          <ui-skeleton v-for="n in 4" :key="n" variant="rect" height="82px" />
        </div>
      </template>

      <div class="preview-grid">
        <div v-for="item in cards" :key="item.label" class="preview-item">
          <p class="label">{{ item.label }}</p>
          <p class="value">{{ item.value }}</p>
        </div>
      </div>

      <div class="preview-actions">
        <ui-button as-link to="/stats" variant="secondary" size="sm">View full stats →</ui-button>
      </div>
    </ui-skeleton-loader>
  </ui-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { apiClient } from '@/api/client'

type UserRole = 'admin' | 'team' | 'jury' | 'organizer'
type TeamRef = { id: number; name: string }
type ProfileLike = {
  role?: UserRole
  is_staff?: boolean
  teams?: TeamRef[]
}

type PlayerStatsResponse = {
  total_tournaments: number
  win_rate: number
  average_evaluation_score: number
  current_team_name: string | null
}

type TeamStatsResponse = {
  active_members_count: number
}

type AdminStatsResponse = {
  total_users: number
  total_tournaments: number
  active_tournaments: number
  new_registrations_last_7_days: number
}

interface Props {
  user?: ProfileLike | null
}

const props = defineProps<Props>()
const isLoading = ref(false)
const isError = ref(false)
const playerStats = ref<PlayerStatsResponse | null>(null)
const teamStats = ref<TeamStatsResponse | null>(null)
const adminStats = ref<AdminStatsResponse | null>(null)

const cards = computed(() => {
  if (props.user?.is_staff) {
    return [
      { label: 'Total users', value: String(adminStats.value?.total_users ?? 0) },
      { label: 'Total tournaments', value: String(adminStats.value?.total_tournaments ?? 0) },
      { label: 'Active tournaments', value: String(adminStats.value?.active_tournaments ?? 0) },
      { label: 'New this week', value: String(adminStats.value?.new_registrations_last_7_days ?? 0) },
    ]
  }

  const base = [
    { label: 'Win rate', value: `${(playerStats.value?.win_rate ?? 0).toFixed(2)}%` },
    { label: 'Total tournaments', value: String(playerStats.value?.total_tournaments ?? 0) },
    { label: 'Average score', value: (playerStats.value?.average_evaluation_score ?? 0).toFixed(2) },
    { label: 'Current team', value: playerStats.value?.current_team_name || 'No team' },
  ]

  if (props.user?.role === 'team') {
    return [...base, { label: 'Active members', value: String(teamStats.value?.active_members_count ?? 0) }]
  }

  return base
})

const loadStats = async () => {
  if (!props.user) return
  isLoading.value = true
  isError.value = false
  playerStats.value = null
  teamStats.value = null
  adminStats.value = null

  try {
    if (props.user.is_staff) {
      const { data } = await apiClient.get<AdminStatsResponse>('/api/stats/admin/')
      adminStats.value = data
      return
    }

    const { data } = await apiClient.get<PlayerStatsResponse>('/api/stats/player/')
    playerStats.value = data

    if (props.user.role === 'team' && props.user.teams?.[0]?.id) {
      const teamRes = await apiClient.get<TeamStatsResponse>(`/api/stats/team/${props.user.teams[0].id}/`)
      teamStats.value = teamRes.data
    }
  } catch {
    isError.value = true
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

.preview-item {
  padding: 0.75rem;
  border-radius: 12px;
  border: 1px solid var(--line-soft);
  background: var(--muted);
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

.preview-actions {
  margin-top: 0.2rem;
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
