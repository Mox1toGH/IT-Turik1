<template>
  <div style="display: grid; gap: 0.75rem">
    <div class="kpi-grid">
      <StatCard label="Total Users" :value="stats.total_users" />
      <StatCard label="Total Teams" :value="stats.total_teams" />
      <StatCard label="Total Tournaments" :value="stats.total_tournaments" />
    </div>

    <div class="stats-grid">
      <div class="stats-card anim-stagger-1">
        <h3>User Growth (30d)</h3>
        <UserGrowthChart :points="growthSeries" />
      </div>

      <div class="stats-card anim-stagger-2">
        <h3>Role Breakdown</h3>
        <RoleBreakdownPie :items="stats.users_by_role" />
      </div>

      <div class="stats-card anim-stagger-3">
        <h3>Active vs Total Tournaments</h3>
        <MembersBarChart :items="tournamentBars" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import StatCard from './StatCard.vue'
import MembersBarChart from './charts/MembersBarChart.vue'
import RoleBreakdownPie from './charts/RoleBreakdownPie.vue'
import UserGrowthChart from './charts/UserGrowthChart.vue'

interface AdminStats {
  total_users: number
  total_teams: number
  total_tournaments: number
  new_registrations_last_7_days: number
  new_registrations_last_30_days: number
  active_tournaments: number
  users_by_role: Array<{ role: string; count: number }>
}
interface Props {
  stats: AdminStats
}
const props = defineProps<Props>()

const tournamentBars = computed(() => [
  { label: 'active', value: props.stats.active_tournaments },
  { label: 'total', value: props.stats.total_tournaments },
])

const growthSeries = computed(() => {
  const day30 = props.stats.new_registrations_last_30_days
  const day7 = props.stats.new_registrations_last_7_days
  const early = Math.max(day30 - day7, 0)
  return [
    { label: 'd-30', value: 0 },
    { label: 'd-24', value: Math.round(early * 0.2) },
    { label: 'd-18', value: Math.round(early * 0.45) },
    { label: 'd-12', value: Math.round(early * 0.7) },
    { label: 'd-6', value: Math.round(early) },
    { label: 'now', value: day30 },
  ]
})
</script>
