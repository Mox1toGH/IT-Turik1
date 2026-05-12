<template>
  <div class="stats-card" :class="staggerClass">
    <h3>{{ label }}</h3>
    <p class="mono-value">{{ value }}</p>
    <p v-if="hint" class="mono-dim">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  label: string
  value: string | number
  hint?: string
  index?: number
}

const props = defineProps<Props>()
const staggerClass = computed(() => `anim-stagger-${Math.min((props.index ?? 0) + 1, 4)}`)
</script>
