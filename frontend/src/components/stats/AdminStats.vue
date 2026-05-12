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
        <UserGrowthChart :points="growthSeries" @select="goUsers" />
      </div>

      <div class="stats-card anim-stagger-2">
        <h3>Role Breakdown</h3>
        <RoleBreakdownPie :items="stats.users_by_role" @select="goRoleCodes" />
      </div>

      <div class="stats-card anim-stagger-3">
        <h3>Active vs Total Tournaments</h3>
        <MembersBarChart :items="tournamentBars" @select="goTournaments" />
      </div>

      <div class="stats-card">
        <h3>Registration Intensity</h3>
        <HeatmapGridChart :cells="registrationHeatmap" @select="goUsers" />
      </div>

      <div class="stats-card">
        <h3>Admin Focus Areas</h3>
        <SegmentedProgressChart :items="focusSegments" @select="goRoleCodes" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import StatCard from './StatCard.vue'
import MembersBarChart from './charts/MembersBarChart.vue'
import RoleBreakdownPie from './charts/RoleBreakdownPie.vue'
import UserGrowthChart from './charts/UserGrowthChart.vue'
import HeatmapGridChart from './charts/HeatmapGridChart.vue'
import SegmentedProgressChart from './charts/SegmentedProgressChart.vue'

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
const router = useRouter()
const goRoleCodes = () => router.push('/admin/role-codes')
const goTournaments = () => router.push('/tournaments')
const goUsers = () => router.push('/profile')

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

const registrationHeatmap = computed(() => {
  const d30 = props.stats.new_registrations_last_30_days
  const d7 = props.stats.new_registrations_last_7_days
  const base = Math.max(Math.round((d30 - d7) / 4), 1)
  return Array.from({ length: 12 }).map((_, idx) => ({
    label: `slot-${idx + 1}`,
    value: idx < 8 ? base + (idx % 3) : Math.max(Math.round(d7 / 4) + (idx % 2), 1),
  }))
})

const focusSegments = computed(() => [
  {
    label: 'Active tournaments',
    percent: Math.min(Math.max((props.stats.active_tournaments / Math.max(props.stats.total_tournaments, 1)) * 100, 0), 100),
  },
  {
    label: '7d growth',
    percent: Math.min(Math.max((props.stats.new_registrations_last_7_days / Math.max(props.stats.new_registrations_last_30_days, 1)) * 100, 0), 100),
  },
  {
    label: 'Team density',
    percent: Math.min(Math.max((props.stats.total_teams / Math.max(props.stats.total_users, 1)) * 100, 0), 100),
  },
])
</script>
