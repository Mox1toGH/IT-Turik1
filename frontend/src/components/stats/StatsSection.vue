<template>
  <section class="stats-shell">
    <h2 class="stats-title">System Stats</h2>

    <ui-query-state v-if="props.user" :query="activeQuery">
      <template #skeleton>
        <div class="stats-grid">
          <div v-for="n in 6" :key="n" class="stats-card loading-card">
            <UiSkeleton variant="rect" height="16px" width="50%" />
            <UiSkeleton variant="rect" height="36px" width="70%" />
            <UiSkeleton variant="rect" height="120px" />
          </div>
        </div>
      </template>

      <template #error>
        <p class="error-text">Unable to load stats right now. Please try again.</p>
      </template>

      <AdminStats v-if="isAdmin && adminStats" :stats="adminStats" />
      <div v-else style="display: grid; gap: 0.75rem">
        <PlayerStats v-if="playerStats" :stats="playerStats" :current-team-to="currentTeamTo" />
        <ui-query-state v-if="isTeamActive" :query="teamQuery">
          <template #skeleton>
            <UiSkeleton variant="rect" height="82px" />
          </template>
          <!-- Team stats are non-fatal: a failure must stay silent. -->
          <template #error />
          <TeamStats v-if="isTeamRole && teamStats" :stats="teamStats" />
        </ui-query-state>
      </div>
    </ui-query-state>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiQueryState from '@/components/ui/UiQueryState'
import PlayerStats from './PlayerStats.vue'
import TeamStats from './TeamStats.vue'
import AdminStats from './AdminStats.vue'
import './styles/stats.css'
import { useGetAdminStats, useGetPlayerStats, useGetTeamStats } from '@/api/stats/stats'
import type { UserSummary } from '@/shared/types/user'

type ProfileLike = UserSummary

interface Props {
  user?: ProfileLike | null
}

const props = defineProps<Props>()

const isAdmin = computed(() => Boolean(props.user?.is_staff))
const isTeamRole = computed(() => props.user?.role === 'team')
const isPlayerActive = computed(() => !!props.user && !isAdmin.value)
const firstTeamId = computed(() => props.user?.teams?.[0]?.id ?? 0)
const isTeamActive = computed(() => isTeamRole.value && firstTeamId.value > 0)

const adminQuery = useGetAdminStats({ query: { enabled: isAdmin } })
const playerQuery = useGetPlayerStats({ query: { enabled: isPlayerActive } })
const teamQuery = useGetTeamStats(firstTeamId, {
  query: { enabled: isTeamActive, retry: false },
})

const { data: adminStats } = adminQuery
const { data: playerStats } = playerQuery
const { data: teamStats } = teamQuery

const activeQuery = computed(() => (isAdmin.value ? adminQuery : playerQuery))

const currentTeamTo = computed(() => {
  const teamName = playerStats.value?.current_team_name
  if (!teamName) return undefined
  const matched = props.user?.teams?.find((team) => team.name === teamName)
  if (matched) return `/teams/${matched.id}`
  const fallbackId = props.user?.teams?.[0]?.id
  return fallbackId ? `/teams/${fallbackId}` : undefined
})
</script>
