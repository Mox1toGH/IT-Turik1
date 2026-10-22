<template>
  <div class="calendar">
    <div class="calendar-nav">
      <ui-button size="sm" variant="ghost" @click="prev">
        <ChevronLeft :size="24" />
      </ui-button>
      <h3 class="calendar-label">{{ navLabel }}</h3>
      <ui-button size="sm" variant="ghost" @click="next">
        <ChevronRight :size="24" />
      </ui-button>

      <div class="view-switcher">
        <button
          v-for="mode in viewModes"
          :key="mode"
          :class="['view-btn', { 'view-btn--active': viewMode === mode }]"
          @click="viewMode = mode"
        >
          {{ mode }}
        </button>
      </div>
    </div>

    <!-- MONTH VIEW -->
    <template v-if="viewMode === 'month'">
      <div class="calendar-grid">
        <div v-for="day in weekDayLabels" :key="day" class="calendar-weekday">{{ day }}</div>

        <calendar-cell
          v-for="cell in monthCells"
          :key="cell.key"
          :cell="cell"
          :selected="isSelectedCell(cell)"
          :max-chips="3"
          :chip-max-length="12"
          @select="handleSelectDay"
          @navigate="navigateToItem"
        />
      </div>
    </template>

    <!-- WEEK VIEW -->
    <template v-if="viewMode === 'week'">
      <div class="calendar-grid calendar-grid--week">
        <div v-for="day in weekDayLabels" :key="day" class="calendar-weekday">{{ day }}</div>

        <calendar-cell
          v-for="cell in weekCells"
          :key="cell.key"
          :cell="cell"
          :selected="isSelectedCell(cell)"
          :max-chips="6"
          :chip-max-length="18"
          week
          @select="handleSelectDay"
          @navigate="navigateToItem"
        />
      </div>
    </template>

    <!-- DAY VIEW -->
    <template v-if="viewMode === 'day'">
      <div class="day-view">
        <div v-if="dayViewItems.length === 0" class="day-view-empty">
          <p class="text-muted">No events for this day</p>
        </div>

        <div v-else class="day-view-list">
          <div
            v-for="item in dayViewItems"
            :key="item.id"
            :class="['day-view-item', `day-view-item--${item.color}`]"
            @click="navigateToItem(item)"
          >
            <div class="day-view-item-header">
              <ui-badge :variant="item.color">{{ typeLabel(item.type) }}</ui-badge>
              <span v-if="item.link" class="day-view-link">
                <a :href="item.link" target="_blank" rel="noopener noreferrer" @click.stop>
                  <ExternalLink class="link-icon" />
                  Join
                </a>
              </span>
              <span v-if="gcalConnected" class="day-view-link">
                <a href="#" @click.stop.prevent="emitExport(item)"
                  ><google-calendar-icon class="link-icon" /> Add to GCal</a
                >
              </span>
            </div>
            <p class="day-view-title">{{ item.title }}</p>
            <p v-if="item.description" class="day-view-description">{{ item.description }}</p>
            <p class="day-view-time text-muted">
              <Clock class="time-icon" />
              {{ formatTime(item.date) }}
            </p>
          </div>
        </div>
      </div>
    </template>

    <calendar-day-sheet
      v-model="isSheetOpen"
      :date="selectedDate"
      :items="selectedDayItems"
      @navigate="navigateToItem"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, toRef } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronLeft, ChevronRight, Clock, ExternalLink } from 'lucide-vue-next'
import GoogleCalendarIcon from '@/icons/GoogleCalendarIcon.vue'
import UiButton from '@/components/ui/UiButton'
import UiBadge from '@/components/ui/UiBadge'
import CalendarCell from './CalendarCell.vue'
import CalendarDaySheet from './CalendarDaySheet.vue'
import {
  WEEK_DAY_LABELS,
  useCalendarGrid,
  type CalendarCellData,
  type CalendarItem,
  type CalendarViewMode,
} from '../composables/useCalendarGrid'
import type { EventResponse, RoundResponse } from '@/api/backendAPINinja.schemas.ts'

interface Props {
  events: EventResponse[]
  rounds: RoundResponse[]
  gcalConnected?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  exportEvent: [eventId: number]
  exportRound: [roundId: number]
}>()
const router = useRouter()

const viewModes: CalendarViewMode[] = ['month', 'week', 'day']
const weekDayLabels = WEEK_DAY_LABELS

const {
  viewMode,
  selectedDate,
  navLabel,
  monthCells,
  weekCells,
  dayViewItems,
  selectedDayItems,
  isSelectedCell,
  selectDay,
  prev,
  next,
  typeLabel,
  formatTime,
} = useCalendarGrid(toRef(props, 'events'), toRef(props, 'rounds'))

const isSheetOpen = ref(false)

function handleSelectDay(cell: CalendarCellData): void {
  selectDay(cell)
  // Touch devices have no hover, so tapping a day with events opens
  // them in a dialog instead of the hover card.
  if (cell.chips.length > 0 && window.matchMedia('(hover: none)').matches) {
    isSheetOpen.value = true
  }
}

function navigateToItem(item: CalendarItem) {
  if (!item.tournamentId) return

  const isRound = item.type === 'round-start' || item.type === 'round-deadline'
  const section = isRound ? 'rounds' : 'schedule'

  router.push({
    path: `/tournaments/${item.tournamentId}`,
    query: { section },
  })
}

function emitExport(item: CalendarItem) {
  const isRound = item.type === 'round-start' || item.type === 'round-deadline'
  const rawId = parseInt(item.id.replace(/^(event-|round-start-|round-deadline-)/, ''))
  if (isRound) {
    emit('exportRound', rawId)
  } else {
    emit('exportEvent', rawId)
  }
}
</script>

<style scoped>
.calendar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.calendar-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.calendar-label {
  flex: 1;
  text-align: center;
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.1rem;
}

.view-switcher {
  display: flex;
  gap: 0;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.view-btn {
  background: var(--card);
  border: none;
  padding: 0.3rem 0.7rem;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  color: var(--muted-foreground);
  transition:
    background 0.15s ease,
    color 0.15s ease;
}

.view-btn:not(:last-child) {
  border-right: 1px solid var(--border);
}

.view-btn--active {
  background: var(--primary);
  color: var(--primary-foreground);
}

.view-btn:hover:not(.view-btn--active) {
  background: var(--subtle);
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.calendar-weekday {
  background: var(--subtle);
  text-align: center;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.5rem 0.25rem;
  color: var(--muted-foreground);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.day-view {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.day-view-empty {
  text-align: center;
  padding: 2rem 0;
}

.day-view-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.day-view-item {
  padding: 0.75rem;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  border-left: 3px solid;
  background: var(--card);
  cursor: pointer;
  transition: background 0.15s ease;
}

.day-view-item:hover {
  background: var(--subtle);
}

.day-view-item--primary {
  border-left-color: var(--primary);
}

.day-view-item--green {
  border-left-color: var(--success);
}

.day-view-item--orange {
  border-left-color: var(--warning);
}

.day-view-item--red {
  border-left-color: var(--destructive);
}

.day-view-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
}

.day-view-link a {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary);
  text-decoration: none;
}

.day-view-link a:hover {
  text-decoration: underline;
}

.link-icon {
  width: 14px;
  height: 14px;
}

.day-view-title {
  font-weight: 600;
  margin: 0 0 0.15rem;
}

.day-view-description {
  font-size: 0.85rem;
  color: var(--muted-foreground);
  margin: 0 0 0.3rem;
}

.day-view-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  margin: 0;
}

.time-icon {
  width: 14px;
  height: 14px;
}

@media (max-width: 768px) {
  .calendar-nav {
    gap: 0.3rem;
  }

  .view-switcher {
    width: 100%;
    order: 10;
  }

  .view-btn {
    flex: 1;
    text-align: center;
  }
}
</style>
