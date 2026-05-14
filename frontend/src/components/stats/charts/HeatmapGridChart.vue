<template>
  <div class="chart-wrap">
    <div class="heatmap-grid">
      <button
        v-for="cell in cells"
        :key="cell.label"
        class="heat-cell"
        :title="`${cell.label}: ${cell.value}`"
        :style="{ opacity: 0.25 + Math.min(cell.value / maxValue, 1) * 0.75 }"
        @click="$emit('select', cell.label)"
      >
        <span>{{ cell.value }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Cell {
  label: string
  value: number
}

const props = defineProps<{ cells: Cell[] }>()
defineEmits<{
  (e: 'select', label: string): void
}>()
const maxValue = computed(() => Math.max(...props.cells.map((cell) => cell.value), 1))
</script>

<style scoped>
.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 6px;
}

.heat-cell {
  border: 1px solid var(--stats-border);
  border-radius: 8px;
  background: var(--stats-accent);
  color: white;
  min-height: 24px;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.heat-cell:hover {
  transform: translateY(-1px);
}

.heat-cell span {
  font-size: 11px;
}
</style>
