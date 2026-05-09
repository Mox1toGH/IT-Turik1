<template>
  <div class="track" :style="{ height: `${height}px` }" role="img" :aria-label="ariaLabel">
    <div class="used" :style="{ width: `${safePercent}%` }">
      <div
        v-for="(segment, index) in segments"
        :key="segment.id"
        class="segment"
        :style="{ width: `${segment.widthPercent}%`, backgroundColor: segment.color || palette[index % palette.length] }"
        :title="segment.title"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Segment {
  id: string | number
  widthPercent: number
  title?: string
  color?: string
}

interface Props {
  percent: number
  segments: Segment[]
  ariaLabel?: string
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  ariaLabel: 'Segmented progress',
  height: 12,
})

const palette = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6', '#f97316']
const safePercent = computed(() => Math.max(0, Math.min(Number(props.percent || 0), 100)))
</script>

<style scoped>
.track {
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--border);
  display: flex;
  background: color-mix(in srgb, var(--muted) 70%, transparent);
}

.used {
  height: 100%;
  display: flex;
  overflow: hidden;
}

.segment {
  height: 100%;
  min-width: 2px;
}
</style>
