<template>
  <ScoreAreaChart :points="points" @select="$emit('select', $event)" />
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
defineEmits<{
  (e: 'select', label: string): void
}>()
</script>
