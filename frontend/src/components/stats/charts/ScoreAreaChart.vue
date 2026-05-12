<template>
  <div class="chart-wrap">
    <svg viewBox="0 0 300 170" width="100%" height="100%">
      <line v-for="line in 4" :key="line" class="grid-line" x1="25" :y1="line * 30" x2="285" :y2="line * 30" />
      <polyline
        fill="var(--stats-accent-soft)"
        stroke="none"
        :points="areaPoints"
      />
      <polyline
        fill="none"
        stroke="var(--stats-accent)"
        stroke-width="2"
        :points="linePoints"
        style="transition: all 1.2s ease"
      />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Point {
  label: string
  value: number
}
interface Props {
  points: Point[]
}

const props = defineProps<Props>()
const max = computed(() => Math.max(...props.points.map((p) => p.value), 1))
const baseY = 140
const minX = 25
const width = 260

const normalized = computed(() =>
  props.points.map((point, index) => {
    const x = minX + (index / Math.max(props.points.length - 1, 1)) * width
    const y = baseY - (point.value / max.value) * 100
    return { x, y }
  }),
)

const linePoints = computed(() => normalized.value.map((p) => `${p.x},${p.y}`).join(' '))
const areaPoints = computed(() => {
  const head = `${minX},${baseY}`
  const body = normalized.value.map((p) => `${p.x},${p.y}`).join(' ')
  const tail = `${minX + width},${baseY}`
  return `${head} ${body} ${tail}`
})
</script>
