<template>
  <ui-modal v-model="isOpen" max-width="420px" scrollable>
    <template #title>{{ formattedDate }}</template>

    <div class="sheet-list">
      <button
        v-for="item in items"
        :key="item.id"
        type="button"
        :class="['sheet-item', `sheet-item--${item.color}`]"
        @click="onPick(item)"
      >
        <span :class="['sheet-dot', `sheet-dot--${item.color}`]"></span>
        <span class="sheet-text">
          <span class="sheet-title">{{ item.title }}</span>
          <span class="sheet-time">{{ formatItemTime(item) }}</span>
        </span>
      </button>
    </div>
  </ui-modal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiModal from '@/components/ui/UiModal'
import type { CalendarItem } from '../composables/useCalendarGrid'

interface Props {
  date: Date | null
  items: CalendarItem[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  navigate: [item: CalendarItem]
}>()

const isOpen = defineModel<boolean>({ default: false })

const formattedDate = computed(
  () =>
    props.date?.toLocaleDateString('uk-UA', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
    }) ?? '',
)

function formatItemTime(item: CalendarItem): string {
  return item.date.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}

function onPick(item: CalendarItem): void {
  isOpen.value = false
  emit('navigate', item)
}
</script>

<style scoped>
.sheet-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sheet-item {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  text-align: left;
  width: 100%;
  padding: 0.65rem 0.7rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  cursor: pointer;
  transition: background 0.15s ease;
}

.sheet-item:hover,
.sheet-item:active {
  background: var(--subtle);
}

.sheet-item--primary {
  border-left: 3px solid var(--primary);
}

.sheet-item--green {
  border-left: 3px solid var(--success);
}

.sheet-item--orange {
  border-left: 3px solid var(--warning);
}

.sheet-item--red {
  border-left: 3px solid var(--destructive);
}

.sheet-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-top: 4px;
  flex-shrink: 0;
}

.sheet-dot--primary {
  background: var(--primary);
}

.sheet-dot--green {
  background: var(--success);
}

.sheet-dot--orange {
  background: var(--warning);
}

.sheet-dot--red {
  background: var(--destructive);
}

.sheet-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.sheet-title {
  font-size: 0.9rem;
  font-weight: 600;
  line-height: 1.35;
}

.sheet-time {
  font-size: 0.8rem;
  color: var(--muted-foreground);
}
</style>
