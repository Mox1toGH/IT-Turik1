<template>
  <div class="calendar">
    <div class="calendar-nav">
      <ui-button size="sm" variant="ghost" @click="prev">
        <arrow-left-icon />
      </ui-button>
      <h3 class="calendar-label">{{ navLabel }}</h3>
      <ui-button size="sm" variant="ghost" @click="next">
        <arrow-right-icon />
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

        <div
          v-for="cell in monthCells"
          :key="cell.key"
          :class="[
            'calendar-cell',
            {
              'calendar-cell--outside': !cell.isCurrentMonth,
              'calendar-cell--today': cell.isToday,
              'calendar-cell--selected': isSelectedCell(cell),
            },
          ]"
          @click="selectDay(cell)"
        >
          <span class="calendar-cell-day">{{ cell.day }}</span>
          <div class="calendar-cell-chips">
            <span
              v-for="chip in cell.chips.slice(0, 3)"
              :key="chip.id"
              :class="['chip', `chip--${chip.color}`, 'chip--clickable']"
              :title="chip.title"
              @click.stop="navigateToItem(chip)"
            >
              {{ truncateText(chip.title, 12) }}
            </span>
            <span v-if="cell.chips.length > 3" class="chip chip--more">
              +{{ cell.chips.length - 3 }}
            </span>
          </div>
        </div>
      </div>

      <calendar-day-detail
        v-if="selectedDate"
        :date="selectedDate"
        :items="selectedDayItems"
        @close="selectedDate = null"
        @navigate="navigateToItem"
      />
    </template>

    <!-- WEEK VIEW -->
    <template v-if="viewMode === 'week'">
      <div class="calendar-grid calendar-grid--week">
        <div v-for="day in weekDayLabels" :key="day" class="calendar-weekday">{{ day }}</div>

        <div
          v-for="cell in weekCells"
          :key="cell.key"
          :class="[
            'calendar-cell',
            'calendar-cell--week',
            {
              'calendar-cell--today': cell.isToday,
              'calendar-cell--selected': isSelectedCell(cell),
            },
          ]"
          @click="selectDay(cell)"
        >
          <span class="calendar-cell-day">{{ cell.dayLabel }}</span>
          <div class="calendar-cell-chips">
            <span
              v-for="chip in cell.chips.slice(0, 6)"
              :key="chip.id"
              :class="['chip', `chip--${chip.color}`, 'chip--clickable']"
              :title="chip.title"
              @click.stop="navigateToItem(chip)"
            >
              {{ truncateText(chip.title, 18) }}
            </span>
            <span v-if="cell.chips.length > 6" class="chip chip--more">
              +{{ cell.chips.length - 6 }}
            </span>
          </div>
        </div>
      </div>

      <calendar-day-detail
        v-if="selectedDate"
        :date="selectedDate"
        :items="selectedDayItems"
        @close="selectedDate = null"
        @navigate="navigateToItem"
      />
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
                  <external-link-icon class="link-icon" />
                  Join
                </a>
              </span>
            </div>
            <p class="day-view-title">{{ item.title }}</p>
            <p v-if="item.description" class="day-view-description">{{ item.description }}</p>
            <p class="day-view-time text-muted">
              <clock-icon class="time-icon" />
              {{ formatTime(item.date) }}
            </p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import ArrowLeftIcon from '@/icons/ArrowLeft.vue'
import ArrowRightIcon from '@/icons/ArrowRight.vue'
import ClockIcon from '@/icons/ClockIcon.vue'
import ExternalLinkIcon from '@/icons/ExternalLinkIcon.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import CalendarDayDetail from './CalendarDayDetail.vue'
import { truncateText } from '@/lib/utils'
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { TournamentEvent, Round } from '@/api/dbTypes'

interface CalendarItem {
  id: string
  title: string
  description: string
  date: Date
  type: 'meet' | 'event' | 'round-start' | 'round-deadline'
  color: 'primary' | 'green' | 'orange' | 'red'
  link?: string
  tournamentId?: number
}

interface Props {
  events: TournamentEvent[]
  rounds: Round[]
}

const props = defineProps<Props>()
const router = useRouter()

type ViewMode = 'month' | 'week' | 'day'
const viewModes: ViewMode[] = ['month', 'week', 'day']
const viewMode = ref<ViewMode>('month')

const today = new Date()
const currentYear = today.getFullYear()
const currentMonth = today.getMonth()

const viewYear = ref(currentYear)
const viewMonth = ref(currentMonth)
const viewDay = ref(today.getDate())
const selectedDate = ref<Date | null>(null)

const weekDayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

const navLabel = computed(() => {
  if (viewMode.value === 'month') {
    return `${monthNames[viewMonth.value]} ${viewYear.value}`
  }
  if (viewMode.value === 'week') {
    const weekStart = getWeekStart(viewYear.value, viewMonth.value, viewDay.value)
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekEnd.getDate() + 6)
    const startFmt = weekStart.toLocaleDateString('uk-UA', { day: 'numeric', month: 'short' })
    const endFmt = weekEnd.toLocaleDateString('uk-UA', { day: 'numeric', month: 'short', year: 'numeric' })
    return `${startFmt} — ${endFmt}`
  }
  const d = new Date(viewYear.value, viewMonth.value, viewDay.value)
  return d.toLocaleDateString('uk-UA', { day: 'numeric', month: 'long', year: 'numeric' })
})

const calendarItems = computed<CalendarItem[]>(() => {
  const items: CalendarItem[] = []

  for (const event of props.events) {
    const date = event.start_datetime instanceof Date
      ? event.start_datetime
      : new Date(event.start_datetime)

    items.push({
      id: `event-${event.id}`,
      title: event.title,
      description: event.description,
      date,
      type: event.type === 'meet' ? 'meet' : 'event',
      color: event.type === 'meet' ? 'primary' : 'green',
      link: event.link || undefined,
      tournamentId: event.tournament,
    })
  }

  for (const round of props.rounds) {
    const startDate = round.start_date instanceof Date
      ? round.start_date
      : new Date(round.start_date)
    const endDate = round.end_date instanceof Date
      ? round.end_date
      : new Date(round.end_date)

    items.push({
      id: `round-start-${round.id}`,
      title: `${round.name} starts`,
      description: '',
      date: startDate,
      type: 'round-start',
      color: 'orange',
      tournamentId: round.tournament,
    })

    items.push({
      id: `round-deadline-${round.id}`,
      title: `${round.name} deadline`,
      description: '',
      date: endDate,
      type: 'round-deadline',
      color: 'red',
      tournamentId: round.tournament,
    })
  }

  return items
})

interface CalendarCell {
  key: string
  day: number
  dayLabel?: string
  date: Date
  isCurrentMonth: boolean
  isToday: boolean
  chips: CalendarItem[]
}

function getItemsForDate(date: Date): CalendarItem[] {
  return calendarItems.value.filter((item) => isSameDay(item.date, date))
}

function isSameDay(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear()
    && a.getMonth() === b.getMonth()
    && a.getDate() === b.getDate()
}

function getWeekStart(y: number, m: number, d: number): Date {
  const date = new Date(y, m, d)
  const dow = (date.getDay() + 6) % 7
  date.setDate(date.getDate() - dow)
  return date
}

const monthCells = computed<CalendarCell[]>(() => {
  const firstDay = new Date(viewYear.value, viewMonth.value, 1)
  const lastDay = new Date(viewYear.value, viewMonth.value + 1, 0)
  const startDow = (firstDay.getDay() + 6) % 7
  const cells: CalendarCell[] = []

  const prevMonthLastDay = new Date(viewYear.value, viewMonth.value, 0)
  for (let i = startDow - 1; i >= 0; i--) {
    const date = new Date(viewYear.value, viewMonth.value - 1, prevMonthLastDay.getDate() - i)
    cells.push({
      key: `prev-${date.getDate()}`,
      day: date.getDate(),
      date,
      isCurrentMonth: false,
      isToday: isSameDay(date, today),
      chips: getItemsForDate(date),
    })
  }

  for (let d = 1; d <= lastDay.getDate(); d++) {
    const date = new Date(viewYear.value, viewMonth.value, d)
    cells.push({
      key: `curr-${d}`,
      day: d,
      date,
      isCurrentMonth: true,
      isToday: isSameDay(date, today),
      chips: getItemsForDate(date),
    })
  }

  const remaining = 42 - cells.length
  for (let d = 1; d <= remaining; d++) {
    const date = new Date(viewYear.value, viewMonth.value + 1, d)
    cells.push({
      key: `next-${d}`,
      day: d,
      date,
      isCurrentMonth: false,
      isToday: isSameDay(date, today),
      chips: getItemsForDate(date),
    })
  }

  return cells
})

const weekCells = computed<CalendarCell[]>(() => {
  const weekStart = getWeekStart(viewYear.value, viewMonth.value, viewDay.value)
  const cells: CalendarCell[] = []

  for (let i = 0; i < 7; i++) {
    const date = new Date(weekStart)
    date.setDate(date.getDate() + i)
    cells.push({
      key: `week-${i}`,
      day: date.getDate(),
      dayLabel: date.toLocaleDateString('uk-UA', { day: 'numeric', month: 'short' }),
      date,
      isCurrentMonth: date.getMonth() === viewMonth.value,
      isToday: isSameDay(date, today),
      chips: getItemsForDate(date),
    })
  }

  return cells
})

const dayViewItems = computed<CalendarItem[]>(() => {
  const d = new Date(viewYear.value, viewMonth.value, viewDay.value)
  return getItemsForDate(d)
})

const selectedDayItems = computed<CalendarItem[]>(() => {
  if (!selectedDate.value) return []
  return getItemsForDate(selectedDate.value)
})

function isSelectedCell(cell: CalendarCell): boolean {
  if (!selectedDate.value) return false
  return isSameDay(cell.date, selectedDate.value)
}

function selectDay(cell: CalendarCell) {
  if (viewMode.value === 'month' || viewMode.value === 'week') {
    if (cell.chips.length > 0) {
      selectedDate.value = cell.date
    } else {
      selectedDate.value = cell.isCurrentMonth ? cell.date : null
    }
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

function typeLabel(type: CalendarItem['type']): string {
  switch (type) {
    case 'meet': return 'Consultation'
    case 'event': return 'Event'
    case 'round-start': return 'Round start'
    case 'round-deadline': return 'Deadline'
  }
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}

function prev() {
  if (viewMode.value === 'month') {
    if (viewMonth.value === 0) {
      viewMonth.value = 11
      viewYear.value--
    } else {
      viewMonth.value--
    }
  } else if (viewMode.value === 'week') {
    const d = new Date(viewYear.value, viewMonth.value, viewDay.value)
    d.setDate(d.getDate() - 7)
    viewYear.value = d.getFullYear()
    viewMonth.value = d.getMonth()
    viewDay.value = d.getDate()
  } else {
    const d = new Date(viewYear.value, viewMonth.value, viewDay.value)
    d.setDate(d.getDate() - 1)
    viewYear.value = d.getFullYear()
    viewMonth.value = d.getMonth()
    viewDay.value = d.getDate()
  }
  selectedDate.value = null
}

function next() {
  if (viewMode.value === 'month') {
    if (viewMonth.value === 11) {
      viewMonth.value = 0
      viewYear.value++
    } else {
      viewMonth.value++
    }
  } else if (viewMode.value === 'week') {
    const d = new Date(viewYear.value, viewMonth.value, viewDay.value)
    d.setDate(d.getDate() + 7)
    viewYear.value = d.getFullYear()
    viewMonth.value = d.getMonth()
    viewDay.value = d.getDate()
  } else {
    const d = new Date(viewYear.value, viewMonth.value, viewDay.value)
    d.setDate(d.getDate() + 1)
    viewYear.value = d.getFullYear()
    viewMonth.value = d.getMonth()
    viewDay.value = d.getDate()
  }
  selectedDate.value = null
}

watch(() => [props.events, props.rounds], () => {
  if (selectedDate.value) {
    const items = getItemsForDate(selectedDate.value)
    if (items.length === 0) {
      selectedDate.value = null
    }
  }
})
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
  transition: background 0.15s ease, color 0.15s ease;
}

.view-btn:not(:last-child) {
  border-right: 1px solid var(--border);
}

.view-btn--active {
  background: var(--primary);
  color: var(--primary-foreground);
}

.view-btn:hover:not(.view-btn--active) {
  background: var(--secondary);
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 1px;
  background: var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.calendar-grid--week .calendar-cell--week {
  min-height: 160px;
}

.calendar-weekday {
  background: var(--secondary);
  text-align: center;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.5rem 0.25rem;
  color: var(--muted-foreground);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

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
  background: var(--secondary);
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

.chip {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 1px 4px;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.chip--clickable {
  cursor: pointer;
}

.chip--clickable:hover {
  filter: brightness(0.9);
}

.chip--primary {
  background: color-mix(in srgb, var(--primary) 15%, transparent);
  color: var(--primary);
}

.chip--green {
  background: rgba(34, 148, 13, 0.12);
  color: #22940d;
}

.chip--orange {
  background: color-mix(in srgb, var(--warning) 15%, transparent);
  color: var(--warning);
}

.chip--red {
  background: color-mix(in srgb, var(--destructive) 12%, transparent);
  color: var(--destructive);
}

.chip--more {
  background: var(--secondary);
  color: var(--muted-foreground);
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
  border-left: 3px solid;
  cursor: pointer;
  transition: background 0.15s ease;
}

.day-view-item:hover {
  filter: brightness(0.97);
}

.day-view-item--primary {
  border-left-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 5%, transparent);
}

.day-view-item--green {
  border-left-color: #22940d;
  background: rgba(34, 148, 13, 0.05);
}

.day-view-item--orange {
  border-left-color: var(--warning);
  background: color-mix(in srgb, var(--warning) 5%, transparent);
}

.day-view-item--red {
  border-left-color: var(--destructive);
  background: color-mix(in srgb, var(--destructive) 5%, transparent);
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
  .calendar-cell {
    min-height: 60px;
    padding: 0.2rem;
  }

  .calendar-cell-day {
    font-size: 0.7rem;
  }

  .chip {
    font-size: 0.55rem;
  }

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
