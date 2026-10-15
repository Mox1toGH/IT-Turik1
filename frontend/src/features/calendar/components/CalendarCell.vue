<template>
  <div
    v-if="cell.chips.length === 0 || !canHover"
    :class="cellClasses"
    @click="$emit('select', cell)"
    tabindex="0"
  >
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

  <ui-hover-card v-else side="bottom" align="center">
    <template #trigger>
      <div :class="cellClasses" @click="$emit('select', cell)" tabindex="0">
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

    <div class="cell-hover-card" @click.stop>
      <div class="cell-hover-header">
        <span class="cell-hover-date">{{ hoverDate }}</span>
        <span class="cell-hover-count">{{ cell.chips.length }}</span>
      </div>
      <div class="cell-hover-list">
        <button
          v-for="item in cell.chips"
          :key="item.id"
          type="button"
          :class="['cell-hover-item', `cell-hover-item--${item.color}`]"
          @click="$emit('navigate', item)"
        >
          <span :class="['cell-hover-dot', `cell-hover-dot--${item.color}`]"></span>
          <span class="cell-hover-text">
            <span class="cell-hover-title">{{ item.title }}</span>
            <span class="cell-hover-time">{{ formatItemTime(item) }}</span>
          </span>
        </button>
      </div>
    </div>
  </ui-hover-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CalendarEventChip from './CalendarEventChip.vue'
import UiHoverCard from '@/components/ui/UiHoverCard'
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

// Touch devices have no hover: the hover card is not rendered at all there
// (tapping a day opens the events dialog instead).
const canHover =
  typeof window !== 'undefined' && typeof window.matchMedia === 'function'
    ? window.matchMedia('(hover: hover)').matches
    : true

const hoverDate = computed(() =>
  props.cell.date.toLocaleDateString('uk-UA', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  }),
)

function formatItemTime(item: CalendarItem): string {
  return item.date.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}
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

.calendar-cell:hover,
.calendar-cell:focus-visible {
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

.cell-hover-card {
  width: 240px;
  max-width: min(240px, 70vw);
}

.cell-hover-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}

.cell-hover-date {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: capitalize;
}

.cell-hover-count {
  font-size: 0.7rem;
  font-weight: 700;
  background: var(--primary);
  color: var(--primary-foreground);
  border-radius: 999px;
  min-width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
}

.cell-hover-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 220px;
  overflow-y: auto;
  overscroll-behavior: contain;
  scrollbar-width: thin;
  padding-right: 2px;
}

.cell-hover-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  text-align: left;
  width: 100%;
  padding: 0.45rem 0.5rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--card);
  cursor: pointer;
  transition: background 0.15s ease;
}

.cell-hover-item:hover {
  background: var(--subtle);
}

.cell-hover-item--primary {
  border-left: 3px solid var(--primary);
}

.cell-hover-item--green {
  border-left: 3px solid var(--success);
}

.cell-hover-item--orange {
  border-left: 3px solid var(--warning);
}

.cell-hover-item--red {
  border-left: 3px solid var(--destructive);
}

.cell-hover-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  margin-top: 5px;
  flex-shrink: 0;
}

.cell-hover-dot--primary {
  background: var(--primary);
}

.cell-hover-dot--green {
  background: var(--success);
}

.cell-hover-dot--orange {
  background: var(--warning);
}

.cell-hover-dot--red {
  background: var(--destructive);
}

.cell-hover-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.cell-hover-title {
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1.3;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.cell-hover-time {
  font-size: 0.7rem;
  color: var(--muted-foreground);
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
