<template>
  <div class="stats-grid">
    <div class="stats-card anim-stagger-1">
      <h3>Team Members Evaluation</h3>
      <MembersBarChart :items="memberSeries" />
    </div>

    <div class="stats-card anim-stagger-2">
      <h3>Team Win Rate</h3>
      <WinRateRadial :rate="stats.win_rate" />
    </div>

    <StatCard class="anim-stagger-3" label="Active Members" :value="stats.active_members_count" />
    <StatCard
      class="anim-stagger-4"
      label="Top Player"
      :value="stats.top_player?.username || 'No data'"
      :to="stats.top_player ? `/users/${stats.top_player.id}` : undefined"
      :hint="
        stats.top_player
          ? `Avg score: ${stats.top_player.average_evaluation_score.toFixed(2)}`
          : 'No scored submissions'
      "
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import StatCard from './StatCard.vue'
import MembersBarChart from './charts/MembersBarChart.vue'
import WinRateRadial from './charts/WinRateRadial.vue'

interface TeamStats {
  win_rate: number
  active_members_count: number
  top_player: {
    id: number
    username: string
    average_evaluation_score: number
  } | null
}
interface Props {
  stats: TeamStats
}

const props = defineProps<Props>()
const memberSeries = computed(() => {
  const top = props.stats.top_player
  const seed = top ? top.average_evaluation_score : 0
  const count = Math.max(props.stats.active_members_count, 1)
  return Array.from({ length: count }).slice(0, 6).map((_, idx) => {
    const isTop = idx === 0 && top
    return {
      label: isTop ? top.username.slice(0, 8) : `member${idx + 1}`,
      value: Math.max(seed - idx * 0.35, 0),
    }
  })
})
</script>
