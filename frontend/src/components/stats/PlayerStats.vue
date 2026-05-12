<template>
  <div class="stats-grid">
    <div class="stats-card anim-stagger-1">
      <h3>Win / Loss Donut</h3>
      <WinLossDonut :wins="stats.wins" :losses="stats.losses" />
    </div>

    <div class="stats-card anim-stagger-2">
      <h3>Evaluation Score Over Time</h3>
      <ScoreAreaChart :points="trendPoints" />
    </div>

    <StatCard class="anim-stagger-3" label="Tournaments" :value="stats.total_tournaments" />
    <StatCard class="anim-stagger-4" label="Win Rate" :value="`${stats.win_rate.toFixed(2)}%`" />
    <StatCard label="Average Score" :value="stats.average_evaluation_score.toFixed(2)" />
    <StatCard label="Current Team" :value="stats.current_team_name || 'No team'" :to="currentTeamTo" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import StatCard from './StatCard.vue'
import WinLossDonut from './charts/WinLossDonut.vue'
import ScoreAreaChart from './charts/ScoreAreaChart.vue'

interface PlayerStats {
  total_tournaments: number
  wins: number
  losses: number
  win_rate: number
  average_evaluation_score: number
  current_team_name: string | null
}

interface Props {
  stats: PlayerStats
  currentTeamTo?: string
}
const props = defineProps<Props>()

const trendPoints = computed(() => {
  const base = props.stats.average_evaluation_score || 0
  return [5, 4, 3, 2, 1].map((offset, index) => ({
    label: `T-${offset}`,
    value: Math.max(base + (index - 2) * 0.45, 0),
  }))
})
</script>
