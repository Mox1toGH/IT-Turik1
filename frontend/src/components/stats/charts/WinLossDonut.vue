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
          :stroke-dasharray="`${winsDash} ${circumference}`"
          stroke-linecap="butt"
          transform="rotate(-90)"
          style="cursor: pointer"
          @mouseenter="hover = 'wins'"
          @mouseleave="hover = null"
          @click="$emit('select', 'wins')"
        />
        <circle
          r="52"
          fill="none"
          stroke="var(--stats-secondary)"
          stroke-width="16"
          :stroke-dasharray="`${lossesDash} ${circumference}`"
          :stroke-dashoffset="`-${winsDash}`"
          stroke-linecap="butt"
          transform="rotate(-90)"
          style="cursor: pointer"
          @mouseenter="hover = 'losses'"
          @mouseleave="hover = null"
          @click="$emit('select', 'losses')"
        />
        <circle
          v-if="hover === 'wins'"
          r="60"
          fill="none"
          stroke="rgba(255,255,255,0.12)"
          stroke-width="1"
        />
        <circle
          v-if="hover === 'losses'"
          r="45"
          fill="none"
          stroke="rgba(255,255,255,0.12)"
          stroke-width="1"
        />
      </g>
      <text x="110" y="88" text-anchor="middle" class="axis-text">{{ centerValue }}</text>
      <text x="110" y="102" text-anchor="middle" class="axis-text">{{ centerLabel }}</text>
      <text x="25" y="160" class="axis-text" style="cursor: pointer" @click="$emit('select', 'wins')">
        W: {{ wins }}
      </text>
      <text x="145" y="160" class="axis-text" style="cursor: pointer" @click="$emit('select', 'losses')">
        L: {{ losses }}
      </text>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Props {
  wins: number
  losses: number
}
defineEmits<{
  (e: 'select', value: 'wins' | 'losses'): void
}>()

const props = defineProps<Props>()
const hover = ref<'wins' | 'losses' | null>(null)
const total = computed(() => Math.max(props.wins + props.losses, 1))
const percent = computed(() => (props.wins / total.value) * 100)
const circumference = 2 * Math.PI * 52
const winsDash = computed(() => (props.wins / total.value) * circumference)
const lossesDash = computed(() => (props.losses / total.value) * circumference)
const centerLabel = computed(() => (hover.value ? hover.value.toUpperCase() : 'WIN RATE'))
const centerValue = computed(() => {
  if (hover.value === 'wins') return String(props.wins)
  if (hover.value === 'losses') return String(props.losses)
  return `${percent.value.toFixed(1)}%`
})
</script>
