<template>
  <div class="calendar">
    <div class="calendar-nav">
      <ui-button size="sm" variant="ghost" @click="prevMonth">
        <arrow-left-icon />
      </ui-button>
      <h3 class="calendar-month-label">{{ monthLabel }}</h3>
      <ui-button size="sm" variant="ghost" @click="nextMonth">
        <arrow-right-icon />
      </ui-button>
    </div>

    <div class="calendar-grid">
      <div v-for="day in weekDayLabels" :key="day" class="calendar-weekday">{{ day }}</div>

      <div
        v-for="cell in calendarCells"
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
            :class="['chip', `chip--${chip.color}`]"
            :title="chip.title"
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
    />
  </div>
</template>

<script setup lang="ts">
import ArrowLeftIcon from '@/icons/ArrowLeft.vue'
import ArrowRightIcon from '@/icons/ArrowRight.vue'
import UiButton from '@/components/ui/UiButton.vue'
import CalendarDayDetail from './CalendarDayDetail.vue'
import { truncateText } from '@/lib/utils'
import { computed, ref, watch } from 'vue'
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

const today = new Date()
const currentYear = today.getFullYear()
const currentMonth = today.getMonth()

const viewYear = ref(currentYear)
const viewMonth = ref(currentMonth)
const selectedDate = ref<Date | null>(null)

const weekDayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

const monthLabel = computed(() => `${monthNames[viewMonth.value]} ${viewYear.value}`)

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
  date: Date
  isCurrentMonth: boolean
  isToday: boolean
  chips: CalendarItem[]
}

function getItemsForDate(date: Date): CalendarItem[] {
  return calendarItems.value.filter((item) => isSameDay(item.date, date))
}

const calendarCells = computed<CalendarCell[]>(() => {
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

const selectedDayItems = computed<CalendarItem[]>(() => {
  if (!selectedDate.value) return []
  return getItemsForDate(selectedDate.value)
})

function isSelectedCell(cell: CalendarCell): boolean {
  if (!selectedDate.value) return false
  return isSameDay(cell.date, selectedDate.value)
}

function selectDay(cell: CalendarCell) {
  if (cell.chips.length > 0) {
    selectedDate.value = cell.date
  } else {
    selectedDate.value = cell.isCurrentMonth ? cell.date : null
  }
}

function prevMonth() {
  if (viewMonth.value === 0) {
    viewMonth.value = 11
    viewYear.value--
  } else {
    viewMonth.value--
  }
  selectedDate.value = null
}

function nextMonth() {
  if (viewMonth.value === 11) {
    viewMonth.value = 0
    viewYear.value++
  } else {
    viewMonth.value++
  }
  selectedDate.value = null
}

function isSameDay(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear()
    && a.getMonth() === b.getMonth()
    && a.getDate() === b.getDate()
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
}

.calendar-month-label {
  flex: 1;
  text-align: center;
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.1rem;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 1px;
  background: var(--border);
  border-radius: var(--radius);
  overflow: hidden;
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
}
</style>
