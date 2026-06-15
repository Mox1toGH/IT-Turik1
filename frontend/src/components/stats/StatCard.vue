<template>
  <div class="stats-card" :class="staggerClass">
    <h3>{{ label }}</h3>
    <p class="mono-value">
      <RouterLink v-if="to" :to="to" class="value-link">{{ value }}</RouterLink>
      <span v-else>{{ value }}</span>
    </p>
    <p v-if="hint" class="mono-dim">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

interface Props {
  label: string
  value: string | number
  hint?: string
  index?: number
  to?: string
}

const props = defineProps<Props>()
const staggerClass = computed(() => `anim-stagger-${Math.min((props.index ?? 0) + 1, 4)}`)
</script>

<style scoped>
.value-link {
  color: inherit;
  text-decoration: none;
  font-weight: inherit;
}

.value-link:hover {
  text-decoration: underline;
}
</style>
