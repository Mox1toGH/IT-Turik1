<template>
  <div class="chart-wrap">
    <div
      v-for="member in sorted"
      :key="member.label"
      style="display: grid; grid-template-columns: 70px 1fr 38px; gap: 8px; align-items: center; margin-bottom: 8px"
    >
      <span class="axis-text">{{ member.label }}</span>
      <div style="height: 10px; border: 1px solid var(--stats-border); border-radius: 999px; overflow: hidden">
        <div
          :style="{ width: `${(member.value / max) * 100}%`, background: 'var(--stats-accent)', height: '100%' }"
        />
      </div>
      <span class="axis-text">{{ member.value.toFixed(1) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Item {
  label: string
  value: number
}
interface Props {
  items: Item[]
}
const props = defineProps<Props>()
const sorted = computed(() => [...props.items].sort((a, b) => b.value - a.value))
const max = computed(() => Math.max(...sorted.value.map((item) => item.value), 1))
</script>
