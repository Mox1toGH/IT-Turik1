<template>
  <div class="chart-wrap">
    <div
      v-for="member in sorted"
      :key="member.label"
      style="display: grid; grid-template-columns: 70px 1fr 38px; gap: 8px; align-items: center; margin-bottom: 8px"
    >
      <span class="axis-text">{{ member.label }}</span>
      <div
        style="height: 10px; border: 1px solid var(--stats-border); border-radius: 999px; overflow: hidden; cursor: pointer"
        @mouseenter="hover = member.label"
        @mouseleave="hover = null"
        @click="$emit('select', member.label)"
      >
        <div
          :style="{
            width: `${(member.value / max) * 100}%`,
            background: hover === member.label ? 'color-mix(in srgb, var(--stats-accent) 82%, white)' : 'var(--stats-accent)',
            height: '100%',
            transition: 'all .2s ease',
          }"
        />
      </div>
      <span class="axis-text">{{ member.value.toFixed(1) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Item {
  label: string
  value: number
}
interface Props {
  items: Item[]
}
defineEmits<{
  (e: 'select', label: string): void
}>()
const props = defineProps<Props>()
const hover = ref<string | null>(null)
const sorted = computed(() => [...props.items].sort((a, b) => b.value - a.value))
const max = computed(() => Math.max(...sorted.value.map((item) => item.value), 1))
</script>
