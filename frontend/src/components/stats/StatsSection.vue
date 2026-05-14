<template>
  <section class="stats-shell">
    <h2 class="stats-title">System Stats</h2>

    <div v-if="isLoading" class="stats-grid">
      <div v-for="n in 6" :key="n" class="stats-card loading-card">
        <UiSkeleton variant="rect" height="16px" width="50%" />
        <UiSkeleton variant="rect" height="36px" width="70%" />
        <UiSkeleton variant="rect" height="120px" />
      </div>
    </div>
    <p v-else-if="isError" class="error-text">Unable to load stats right now. Please try again.</p>

    <template v-else>
      <AdminStats v-if="isAdmin && adminStats" :stats="adminStats" />
      <div v-else style="display: grid; gap: 0.75rem">
        <PlayerStats v-if="playerStats" :stats="playerStats" :current-team-to="currentTeamTo" />
        <TeamStats v-if="isTeamRole && teamStats" :stats="teamStats" />
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { apiClient } from '@/api/client'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import PlayerStats from './PlayerStats.vue'
import TeamStats from './TeamStats.vue'
import AdminStats from './AdminStats.vue'
import './styles/stats.css'

type UserRole = 'admin' | 'team' | 'jury' | 'organizer'
type TeamRef = { id: number; name: string }
type ProfileLike = {
  role?: UserRole
  is_staff?: boolean
  teams?: TeamRef[]
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
    id: number
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
const playerStats = ref<PlayerStatsResponse | null>(null)
const teamStats = ref<TeamStatsResponse | null>(null)
const adminStats = ref<AdminStatsResponse | null>(null)

const isAdmin = computed(() => Boolean(props.user?.is_staff))
const isTeamRole = computed(() => props.user?.role === 'team')
const currentTeamTo = computed(() => {
  const teamName = playerStats.value?.current_team_name
  if (!teamName) return undefined
  const matched = props.user?.teams?.find((team) => team.name === teamName)
  if (matched) return `/teams/${matched.id}`
  const fallbackId = props.user?.teams?.[0]?.id
  return fallbackId ? `/teams/${fallbackId}` : undefined
})

const loadStats = async () => {
  if (!props.user) return
  isLoading.value = true
  isError.value = false
  playerStats.value = null
  teamStats.value = null
  adminStats.value = null

  try {
    if (isAdmin.value) {
      const { data } = await apiClient.get<AdminStatsResponse>('/api/stats/admin/')
      adminStats.value = data
      return
    }

    const { data } = await apiClient.get<PlayerStatsResponse>('/api/stats/player/')
    playerStats.value = data

    if (isTeamRole.value) {
      const teamId = props.user.teams?.[0]?.id
      if (!teamId) return
      const teamResponse = await apiClient.get<TeamStatsResponse>(`/api/stats/team/${teamId}/`)
      teamStats.value = teamResponse.data
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
