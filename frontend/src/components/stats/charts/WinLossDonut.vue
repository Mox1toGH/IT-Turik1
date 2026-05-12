<template>
  <div class="chart-wrap">
    <svg viewBox="0 0 220 170" width="100%" height="100%">
      <g transform="translate(110,85)">
        <circle r="52" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="16" />
        <circle
          r="52"
          fill="none"
          stroke="var(--stats-accent)"
          stroke-width="16"
          :stroke-dasharray="`${dash} ${circumference}`"
          stroke-linecap="butt"
          transform="rotate(-90)"
          style="transition: stroke-dasharray 1.2s ease"
        />
      </g>
      <text x="110" y="90" text-anchor="middle" class="axis-text">{{ percent.toFixed(1) }}%</text>
      <text x="25" y="160" class="axis-text">W: {{ wins }}</text>
      <text x="145" y="160" class="axis-text">L: {{ losses }}</text>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  wins: number
  losses: number
}
const props = defineProps<Props>()
const total = computed(() => Math.max(props.wins + props.losses, 1))
const percent = computed(() => (props.wins / total.value) * 100)
const circumference = 2 * Math.PI * 52
const dash = computed(() => (percent.value / 100) * circumference)
</script>
