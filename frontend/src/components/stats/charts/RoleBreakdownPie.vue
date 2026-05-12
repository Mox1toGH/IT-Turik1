<template>
  <div class="chart-wrap">
    <svg viewBox="0 0 260 170" width="100%" height="100%">
      <g transform="translate(85,85)">
        <template v-for="(slice, idx) in slices" :key="slice.role">
          <path :d="slice.path" :fill="colors[idx % colors.length]" />
        </template>
        <circle r="26" fill="var(--stats-card)" />
      </g>
      <g transform="translate(150,45)">
        <text
          v-for="(slice, idx) in slices"
          :key="`${slice.role}-label`"
          x="0"
          :y="idx * 18"
          class="axis-text"
          :fill="colors[idx % colors.length]"
        >
          {{ slice.role }}: {{ slice.count }}
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Item {
  role: string
  count: number
}
interface Props {
  items: Item[]
}

const props = defineProps<Props>()
const colors = ['var(--stats-accent)', 'var(--stats-secondary)', '#6a6a6a', '#8a8a8a']

const total = computed(() => Math.max(props.items.reduce((sum, item) => sum + item.count, 0), 1))

const polarToCartesian = (r: number, angle: number) => ({
  x: r * Math.cos((angle * Math.PI) / 180),
  y: r * Math.sin((angle * Math.PI) / 180),
})

const slices = computed(() => {
  let start = -90
  return props.items.map((item) => {
    const sweep = (item.count / total.value) * 360
    const end = start + sweep
    const outerR = 52
    const s = polarToCartesian(outerR, start)
    const e = polarToCartesian(outerR, end)
    const largeArc = sweep > 180 ? 1 : 0
    const path = `M 0 0 L ${s.x} ${s.y} A ${outerR} ${outerR} 0 ${largeArc} 1 ${e.x} ${e.y} Z`
    const result = { role: item.role, count: item.count, path }
    start = end
    return result
  })
})
</script>
