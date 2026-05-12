<template>
  <ScoreAreaChart :points="points" />
</template>

<script setup lang="ts">
import ScoreAreaChart from './ScoreAreaChart.vue'

interface Point {
  label: string
  value: number
}
interface Props {
  points: Point[]
}
defineProps<Props>()
</script>
