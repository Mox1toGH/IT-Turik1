<template>
  <div class="chart-wrap">
    <svg viewBox="0 0 220 170" width="100%" height="100%">
      <g transform="translate(110,85)">
        <circle r="50" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="12" />
        <circle
          r="50"
          fill="none"
          stroke="var(--stats-accent)"
          stroke-width="12"
          :stroke-dasharray="`${dash} ${circumference}`"
          transform="rotate(-90)"
          style="transition: stroke-dasharray 1.2s ease"
        />
      </g>
      <text x="110" y="90" text-anchor="middle" class="axis-text">{{ rate.toFixed(1) }}%</text>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  rate: number
}
const props = defineProps<Props>()
const rate = computed(() => Math.min(Math.max(props.rate, 0), 100))
const circumference = 2 * Math.PI * 50
const dash = computed(() => (rate.value / 100) * circumference)
</script>
