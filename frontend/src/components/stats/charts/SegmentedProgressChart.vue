<template>
  <div class="chart-wrap">
    <div style="display: grid; gap: 10px; padding-top: 6px">
      <div
        v-for="item in items"
        :key="item.label"
        style="display: grid; grid-template-columns: 120px 1fr 44px; gap: 8px; align-items: center"
      >
        <span class="axis-text">{{ item.label }}</span>
        <div
          style="height: 12px; border-radius: 999px; background: rgba(255,255,255,.06); overflow: hidden; cursor: pointer"
          @click="$emit('select', item.label)"
        >
          <div
            :style="{
              width: `${Math.min(Math.max(item.percent, 0), 100)}%`,
              height: '100%',
              background: 'var(--stats-accent)',
              transition: 'width .5s ease',
            }"
          />
        </div>
        <span class="axis-text">{{ item.percent.toFixed(0) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Item {
  label: string
  percent: number
}

defineProps<{ items: Item[] }>()
defineEmits<{
  (e: 'select', label: string): void
}>()
</script>
