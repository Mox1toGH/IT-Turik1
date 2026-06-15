<template>
  <div class="stats-grid">
    <div class="stats-card anim-stagger-1">
      <h3>Win / Loss Donut</h3>
      <WinLossDonut :wins="stats.wins" :losses="stats.losses" @select="goTournaments" />
    </div>

    <div class="stats-card anim-stagger-2">
      <div class="card-head">
        <h3>Evaluation Dynamics</h3>
        <button class="chip" @click="mode = mode === 'area' ? 'heat' : 'area'">
          {{ mode === 'area' ? 'Heatmap' : 'Area' }}
        </button>
      </div>
      <ScoreAreaChart v-if="mode === 'area'" :points="trendPoints" @select="goTournaments" />
      <HeatmapGridChart v-else :cells="heatCells" @select="goTournaments" />
    </div>

    <div class="stats-card">
      <h3>Performance Segments</h3>
      <SegmentedProgressChart :items="progressItems" @select="goTournaments" />
    </div>

    <StatCard class="anim-stagger-3" label="Tournaments" :value="stats.total_tournaments" />
    <StatCard class="anim-stagger-4" label="Win Rate" :value="`${stats.win_rate.toFixed(2)}%`" />
    <StatCard label="Average Score" :value="stats.average_evaluation_score.toFixed(2)" />
    <StatCard label="Current Team" :value="stats.current_team_name || 'No team'" :to="currentTeamTo" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import StatCard from './StatCard.vue'
import WinLossDonut from './charts/WinLossDonut.vue'
import ScoreAreaChart from './charts/ScoreAreaChart.vue'
import SegmentedProgressChart from './charts/SegmentedProgressChart.vue'
import HeatmapGridChart from './charts/HeatmapGridChart.vue'

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
const router = useRouter()
const mode = ref<'area' | 'heat'>('area')
const goTournaments = () => {
  router.push('/tournaments')
}

const trendPoints = computed(() => {
  const base = props.stats.average_evaluation_score || 0
  return [5, 4, 3, 2, 1].map((offset, index) => ({
    label: `T-${offset}`,
    value: Math.max(base + (index - 2) * 0.45, 0),
  }))
})

const progressItems = computed(() => [
  { label: 'Win rate', percent: Math.min(Math.max(props.stats.win_rate, 0), 100) },
  {
    label: 'Avg score',
    percent: Math.min(Math.max((props.stats.average_evaluation_score / 10) * 100, 0), 100),
  },
  {
    label: 'Activity',
    percent: Math.min(Math.max((props.stats.total_tournaments / 12) * 100, 0), 100),
  },
])

const heatCells = computed(() =>
  trendPoints.value.map((point, idx) => ({
    label: point.label,
    value: Math.round(point.value * 10 + idx),
  })),
)
</script>

<style scoped>
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
}

.chip {
  border: 1px solid var(--stats-border);
  background: transparent;
  color: var(--stats-muted);
  border-radius: 999px;
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  cursor: pointer;
}
</style>
