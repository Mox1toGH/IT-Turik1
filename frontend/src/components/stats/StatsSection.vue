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
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import PlayerStats from './PlayerStats.vue'
import TeamStats from './TeamStats.vue'
import AdminStats from './AdminStats.vue'
import './styles/stats.css'
import { getAdminStats, getPlayerStats, getTeamStats } from '@/api/stats/stats'

import type { User, AdminStats as AdminStatsResponse, PlayerStats as PlayerStatsResponse, TeamStats as TeamStatsResponse } from '@/api/.ts.schemas'

type ProfileLike = User

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
      const data = await getAdminStats()
      adminStats.value = data
      return
    }

    const data = await getPlayerStats()
    playerStats.value = data

    if (isTeamRole.value) {
      const teamId = props.user.teams?.[0]?.id
      if (!teamId) return
      const data = await getTeamStats(teamId)
      teamStats.value = data
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
