<template>
  <div :class="cellClasses" @click="$emit('select', cell)">
    <span class="calendar-cell-day">{{ cell.dayLabel ?? cell.day }}</span>
    <div class="calendar-cell-chips">
      <calendar-event-chip
        v-for="chip in visibleChips"
        :key="chip.id"
        :chip="chip"
        :max-length="chipMaxLength"
        @navigate="$emit('navigate', $event)"
      />
      <span v-if="overflowCount > 0" class="chip chip--more">+{{ overflowCount }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CalendarEventChip from './CalendarEventChip.vue'
import type { CalendarCellData, CalendarItem } from '../composables/useCalendarGrid'

interface Props {
  cell: CalendarCellData
  selected?: boolean
  maxChips?: number
  chipMaxLength?: number
  week?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  maxChips: 3,
  chipMaxLength: 12,
  week: false,
})

defineEmits<{
  select: [cell: CalendarCellData]
  navigate: [item: CalendarItem]
}>()

const cellClasses = computed(() => [
  'calendar-cell',
  {
    'calendar-cell--week': props.week,
    'calendar-cell--outside': !props.cell.isCurrentMonth,
    'calendar-cell--today': props.cell.isToday,
    'calendar-cell--selected': props.selected,
  },
])

const visibleChips = computed(() => props.cell.chips.slice(0, props.maxChips))
const overflowCount = computed(() => Math.max(props.cell.chips.length - props.maxChips, 0))
</script>

<style scoped>
.calendar-cell {
  background: var(--card);
  min-height: 90px;
  padding: 0.35rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  cursor: pointer;
  transition: background 0.15s ease;
}

.calendar-cell:hover {
  background: var(--subtle);
}

.calendar-cell--week {
  min-height: 160px;
}

.calendar-cell--outside {
  opacity: 0.4;
}

.calendar-cell--today .calendar-cell-day {
  background: var(--primary);
  color: var(--primary-foreground);
  border-radius: 999px;
  width: 22px;
  height: 22px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.calendar-cell--selected {
  background: color-mix(in srgb, var(--primary) 8%, transparent);
  outline: 2px solid var(--primary);
  outline-offset: -2px;
}

.calendar-cell-day {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--foreground);
}

.calendar-cell-chips {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.chip--more {
  background: var(--subtle);
  color: var(--muted-foreground);
  font-size: 0.65rem;
  font-weight: 600;
  padding: 1px 4px;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .calendar-cell {
    min-height: 60px;
    padding: 0.2rem;
  }

  .calendar-cell-day {
    font-size: 0.7rem;
  }

  .chip--more {
    font-size: 0.55rem;
  }
}
</style>
