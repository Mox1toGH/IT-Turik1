import { computed, ref, watch, type ComputedRef, type Ref } from 'vue'
import type { EventResponse, RoundResponse } from '@/api/backendAPINinja.schemas.ts'

export interface CalendarItem {
  id: string
  title: string
  description: string
  date: Date
  type: 'meet' | 'event' | 'round-start' | 'round-deadline'
  color: 'primary' | 'green' | 'orange' | 'red'
  link?: string
  tournamentId?: number
}

export interface CalendarCellData {
  key: string
  day: number
  dayLabel?: string
  date: Date
  isCurrentMonth: boolean
  isToday: boolean
  chips: CalendarItem[]
}

export type CalendarViewMode = 'month' | 'week' | 'day'

export interface CalendarGrid {
  viewMode: Ref<CalendarViewMode>
  viewYear: Ref<number>
  viewMonth: Ref<number>
  viewDay: Ref<number>
  selectedDate: Ref<Date | null>
  navLabel: ComputedRef<string>
  monthCells: ComputedRef<CalendarCellData[]>
  weekCells: ComputedRef<CalendarCellData[]>
  dayViewItems: ComputedRef<CalendarItem[]>
  selectedDayItems: ComputedRef<CalendarItem[]>
  isSelectedCell: (cell: CalendarCellData) => boolean
  selectDay: (cell: CalendarCellData) => void
  prev: () => void
  next: () => void
  typeLabel: (type: CalendarItem['type']) => string
  formatTime: (date: Date) => string
}

const WEEK_DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const MONTH_NAMES = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
]

export function isSameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  )
}

export function getWeekStart(y: number, m: number, d: number): Date {
  const date = new Date(y, m, d)
  const dow = (date.getDay() + 6) % 7
  date.setDate(date.getDate() - dow)
  return date
}

export function useCalendarGrid(
  events: Ref<EventResponse[]>,
  rounds: Ref<RoundResponse[]>,
): CalendarGrid {
  const today = new Date()
  const viewMode = ref<CalendarViewMode>('month')
  const viewYear = ref<number>(today.getFullYear())
  const viewMonth = ref<number>(today.getMonth())
  const viewDay = ref<number>(today.getDate())
  const selectedDate = ref<Date | null>(null)

  const navLabel = computed<string>(() => {
    if (viewMode.value === 'month') {
      return `${MONTH_NAMES[viewMonth.value]} ${viewYear.value}`
    }
    if (viewMode.value === 'week') {
      const weekStart = getWeekStart(viewYear.value, viewMonth.value, viewDay.value)
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekEnd.getDate() + 6)
      const startFmt = weekStart.toLocaleDateString('uk-UA', { day: 'numeric', month: 'short' })
      const endFmt = weekEnd.toLocaleDateString('uk-UA', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      })
      return `${startFmt} — ${endFmt}`
    }
    const d = new Date(viewYear.value, viewMonth.value, viewDay.value)
    return d.toLocaleDateString('uk-UA', { day: 'numeric', month: 'long', year: 'numeric' })
  })

  const calendarItems = computed<CalendarItem[]>(() => {
    const items: CalendarItem[] = []

    for (const event of events.value) {
      const date = new Date(event.start_datetime)

      items.push({
        id: `event-${event.id}`,
        title: event.title,
        description: event.description ?? '-',
        date,
        type: event.type === 'meet' ? 'meet' : 'event',
        color: event.type === 'meet' ? 'primary' : 'green',
        link: event.link || undefined,
        tournamentId: event.tournament,
      })
    }

    for (const round of rounds.value) {
      const startDate = new Date(round.start_date)
      const endDate = new Date(round.end_date)

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

  function getItemsForDate(date: Date): CalendarItem[] {
    return calendarItems.value.filter((item) => isSameDay(item.date, date))
  }

  const monthCells = computed<CalendarCellData[]>(() => {
    const lastDay = new Date(viewYear.value, viewMonth.value + 1, 0)
    const firstDay = new Date(viewYear.value, viewMonth.value, 1)
    const startDow = (firstDay.getDay() + 6) % 7
    const cells: CalendarCellData[] = []

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

  const weekCells = computed<CalendarCellData[]>(() => {
    const weekStart = getWeekStart(viewYear.value, viewMonth.value, viewDay.value)
    const cells: CalendarCellData[] = []

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

  function isSelectedCell(cell: CalendarCellData): boolean {
    if (!selectedDate.value) return false
    return isSameDay(cell.date, selectedDate.value)
  }

  function selectDay(cell: CalendarCellData): void {
    if (viewMode.value === 'month' || viewMode.value === 'week') {
      if (cell.chips.length > 0) {
        selectedDate.value = cell.date
      } else {
        selectedDate.value = cell.isCurrentMonth ? cell.date : null
      }
    }
  }

  function typeLabel(type: CalendarItem['type']): string {
    switch (type) {
      case 'meet':
        return 'Consultation'
      case 'event':
        return 'Event'
      case 'round-start':
        return 'Round start'
      case 'round-deadline':
        return 'Deadline'
    }
  }

  function formatTime(date: Date): string {
    return date.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
  }

  function prev(): void {
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

  function next(): void {
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

  watch([events, rounds], () => {
    if (selectedDate.value) {
      const items = getItemsForDate(selectedDate.value)
      if (items.length === 0) {
        selectedDate.value = null
      }
    }
  })

  return {
    viewMode,
    viewYear,
    viewMonth,
    viewDay,
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
  }
}

export { WEEK_DAY_LABELS }
