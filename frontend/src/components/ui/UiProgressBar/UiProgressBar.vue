<template>
  <div class="track" :style="{ height: `${height}px` }" role="progressbar" :aria-valuemin="0" :aria-valuemax="100" :aria-valuenow="safePercent">
    <div class="fill" :style="{ width: `${safePercent}%`, background: fillColor }" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  percent: number
  height?: number
  fillColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: 12,
  fillColor: 'var(--muted-foreground)',
})

const safePercent = computed(() => Math.max(0, Math.min(Number(props.percent || 0), 100)))
</script>

<style scoped>
.track {
  width: 100%;
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--border);
  background: var(--track);
}

.fill {
  height: 100%;
}
</style>
