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

const palette = [
  'var(--chart-1)',
  'var(--chart-2)',
  'var(--chart-3)',
  'var(--chart-4)',
  'var(--chart-5)',
  'var(--chart-6)',
]
const safePercent = computed(() => Math.max(0, Math.min(Number(props.percent || 0), 100)))
</script>

<style scoped>
.track {
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--border);
  display: flex;
  background: var(--track);
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
