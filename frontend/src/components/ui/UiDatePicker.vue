<template>
  <div class="datepicker-wrapper" :class="{ open: isOpen }" ref="wrapperRef">
    <ui-button
      variant="ghost"
      :class="['datepicker-trigger', { invalid: !!props.isInvalid }]"
      :aria-invalid="props.isInvalid ? 'true' : 'false'"
      :disabled="disabled"
      @click="toggleOpen"
      @keydown="handleTriggerKeydown"
      :aria-expanded="isOpen"
      aria-haspopup="dialog"
    >
      <CalendarIcon class="datepicker-icon" />
      <span class="datepicker-value">{{ displayValue }}</span>
      <arrow-down class="datepicker-chevron" />
    </ui-button>

    <Transition name="dropdown">
      <div
        v-if="isOpen"
        class="datepicker-dropdown"
        :class="dropdownPosition"
        tabindex="-1"
        ref="dropdownRef"
        role="dialog"
        aria-label="Date picker"
        @keydown="handleDropdownKeydown"
      >
        <div class="dp-header">
          <ui-button class="dp-nav-btn" @click="adjustMonth(-1)" aria-label="Previous">
            <ArrowLeft />
          </ui-button>

          <div class="dp-header-center">
            <ui-button
              class="dp-month-btn"
              data-testid="month-pick-btn"
              @click="viewMode = viewMode === 'month' ? 'days' : 'month'"
            >
              {{ monthNames[viewMonth] }}
            </ui-button>
            <ui-button
              class="dp-year-btn"
              data-testid="year-pick-btn"
              @click="viewMode = viewMode === 'year' ? 'days' : 'year'"
            >
              {{ viewYear }}
            </ui-button>
          </div>

          <ui-button class="dp-nav-btn" @click="adjustMonth(1)" aria-label="Next">
            <ArrowRight />
          </ui-button>
        </div>

        <template v-if="viewMode === 'days'">
          <div class="dp-weekdays">
            <span v-for="day in weekdays" :key="day" class="dp-weekday">{{ day }}</span>
          </div>

          <div class="dp-days" data-testid="day-pick-grid" role="grid">
            <ui-button
              v-for="cell in calendarCells"
              :key="cell.date.toISOString()"
              class="dp-day"
              :class="getCellClasses(cell)"
              :tabindex="cell.isCurrentMonth ? 0 : -1"
              :aria-selected="cell.isSelected"
              :disabled="cell.isDisabled"
              @click="handleDateClick(cell.date)"
              @mouseenter="hoverDate = range ? cell.date : null"
              @mouseleave="hoverDate = null"
            >
              {{ cell.date.getDate() }}
            </ui-button>
          </div>
        </template>

        <div v-if="viewMode === 'month'" class="dp-month-grid" data-testid="month-pick-grid">
          <ui-button
            v-for="(name, idx) in monthNames"
            :key="name"
            class="dp-month-item"
            :class="{ selected: idx === viewMonth }"
            @click="selectMonth(idx)"
          >
            {{ name.slice(0, 3) }}
          </ui-button>
        </div>

        <div
          v-if="viewMode === 'year'"
          class="dp-year-grid"
          data-testid="year-pick-grid"
          ref="yearGridRef"
        >
          <ui-button
            v-for="year in yearRange"
            :key="year"
            class="dp-year-item"
            :class="{ selected: year === viewYear }"
            @click="selectYear(year)"
          >
            {{ year }}
          </ui-button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import UiButton from './UiButton.vue'
import ArrowRight from '@/icons/ArrowRight.vue'
import ArrowLeft from '@/icons/ArrowLeft.vue'
import CalendarIcon from '@/icons/CalendarIcon.vue'
import ArrowDown from '@/icons/ArrowDown.vue'
import { formatDate } from '@/lib/date'

export interface DateRange {
  start: Date | null
  end: Date | null
}

type ViewMode = 'days' | 'month' | 'year'

interface CalendarCell {
  date: Date
  isCurrentMonth: boolean
  isToday: boolean
  isDisabled: boolean
  isSelected: boolean
  inRange: boolean
  isRangeStart: boolean
  isRangeEnd: boolean
}

type Props =
  | {
      range?: false
      modelValue?: Date | null
      placeholder?: string
      disabled?: boolean
      minDate?: Date
      maxDate?: Date
      isInvalid?: boolean
    }
  | {
      range: true
      modelValue?: DateRange | null
      placeholder?: string
      disabled?: boolean
      minDate?: Date
      maxDate?: Date
      isInvalid?: boolean
    }

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Pick a date',
  disabled: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: Date | DateRange | null): void
  (e: 'blur'): void
}>()

const isOpen = ref(false)
const viewMode = ref<ViewMode>('days')
const viewYear = ref(new Date().getFullYear())
const viewMonth = ref(new Date().getMonth())
const hoverDate = ref<Date | null>(null)
const rangeStartInternal = ref<Date | null>(null)
const dropdownRef = ref<HTMLDivElement | null>(null)
const wrapperRef = ref<HTMLDivElement | null>(null)
const dropdownPosition = ref<'bottom' | 'top'>('bottom')

// Acessability
function calculateDropdownPosition() {
  if (!wrapperRef.value || !dropdownRef.value) return

  const triggerRect = wrapperRef.value.getBoundingClientRect()
  const viewportHeight = window.innerHeight
  const dropdownHeight = dropdownRef.value.getBoundingClientRect().height

  const spaceBelow = viewportHeight - triggerRect.bottom
  const spaceAbove = triggerRect.top

  dropdownPosition.value =
    spaceBelow >= dropdownHeight || spaceBelow >= spaceAbove ? 'bottom' : 'top'
}

function handleTriggerKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault()
    toggleOpen()
  } else if (e.key === 'Escape') {
    if (isOpen.value) emit('blur')
    isOpen.value = false
  } else if (e.key === 'ArrowDown' && !isOpen.value) {
    e.preventDefault()
    isOpen.value = true
  }
}

function handleDropdownKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    if (isOpen.value) emit('blur')
    isOpen.value = false
    return
  }

  if (viewMode.value !== 'days') return

  const focusable = dropdownRef.value?.querySelectorAll<HTMLElement>(
    '.dp-day:not([disabled]):not([tabindex="-1"])',
  )
  if (!focusable?.length) return

  const focused = document.activeElement as HTMLElement
  const idx = Array.from(focusable).indexOf(focused)

  const move = (delta: number) => {
    e.preventDefault()
    const next = focusable[idx + delta]
    next?.focus()
  }

  switch (e.key) {
    case 'ArrowRight':
      move(1)
      break
    case 'ArrowLeft':
      move(-1)
      break
    case 'ArrowDown':
      move(7)
      break
    case 'ArrowUp':
      move(-7)
      break
    case 'Enter':
    case ' ':
      e.preventDefault()
      focused?.click()
      break
  }
}

// Constants & Utils
const weekdays = ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
const monthNames = Array.from({ length: 12 }, (_, i) =>
  new Intl.DateTimeFormat('uk-UA', { month: 'long' }).format(new Date(2026, i, 1)),
)

const isSameDay = (date1: Date, date2: Date) =>
  date1.getFullYear() === date2.getFullYear() &&
  date1.getMonth() === date2.getMonth() &&
  date1.getDate() === date2.getDate()

const normalizeDate = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate())

// Computed

const displayValue = computed(() => {
  if (props.range) {
    const start = props.modelValue?.start
    const end = props.modelValue?.end
    if (!start) return props.placeholder
    return end ? `${formatDate(start)} – ${formatDate(end)}` : `${formatDate(start)} – ...`
  }

  return props.modelValue ? formatDate(props.modelValue as Date) : props.placeholder
})

const calendarCells = computed(() => {
  const cells = []
  const firstDayOfMonth = new Date(viewYear.value, viewMonth.value, 1)
  const lastDayOfMonth = new Date(viewYear.value, viewMonth.value + 1, 0)

  // Padding from previous month
  const startPadding = firstDayOfMonth.getDay()
  for (let i = startPadding; i > 0; i--) {
    cells.push({ date: new Date(viewYear.value, viewMonth.value, 1 - i), isCurrentMonth: false })
  }

  // Current month days
  for (let i = 1; i <= lastDayOfMonth.getDate(); i++) {
    cells.push({ date: new Date(viewYear.value, viewMonth.value, i), isCurrentMonth: true })
  }

  // Padding for next month (to keep 6 rows / 42 cells)
  const endPadding = 42 - cells.length
  for (let i = 1; i <= endPadding; i++) {
    cells.push({ date: new Date(viewYear.value, viewMonth.value + 1, i), isCurrentMonth: false })
  }

  return cells.map((cell) => ({
    ...cell,
    isToday: isSameDay(cell.date, new Date()),
    isDisabled: isDateDisabled(cell.date),
    ...calculateRangeStates(cell.date),
  }))
})

const yearRange = computed(() => {
  const years = []
  for (let i = viewYear.value - 7; i <= viewYear.value + 4; i++) years.push(i)
  return years
})

// Methods

function isDateDisabled(date: Date) {
  if (props.minDate && normalizeDate(date) < normalizeDate(props.minDate)) return true
  if (props.maxDate && normalizeDate(date) > normalizeDate(props.maxDate)) return true
  return false
}

function calculateRangeStates(date: Date) {
  if (!props.range) {
    const isSelected = props.modelValue ? isSameDay(date, props.modelValue as Date) : false
    return { isSelected, inRange: false, isRangeStart: isSelected, isRangeEnd: isSelected }
  }

  const start = rangeStartInternal.value || props.modelValue?.start
  const end = rangeStartInternal.value ? hoverDate.value : props.modelValue?.end

  if (!start) return { isSelected: false, inRange: false, isRangeStart: false, isRangeEnd: false }

  const isRangeStart = isSameDay(date, start)
  const isRangeEnd = end ? isSameDay(date, end) : false

  let inRange = false
  if (start && end) {
    const min = Math.min(start.getTime(), end.getTime())
    const max = Math.max(start.getTime(), end.getTime())
    inRange = date.getTime() > min && date.getTime() < max
  }

  return { isSelected: isRangeStart || isRangeEnd, inRange, isRangeStart, isRangeEnd }
}

function handleDateClick(date: Date) {
  if (isDateDisabled(date)) return

  if (!props.range) {
    emit('update:modelValue', date)
    isOpen.value = false
    emit('blur')
  } else {
    if (!rangeStartInternal.value) {
      rangeStartInternal.value = date
    } else {
      const date1 = rangeStartInternal.value
      const date2 = date
      emit('update:modelValue', {
        start: date1 < date2 ? date1 : date2,
        end: date1 < date2 ? date2 : date1,
      })
      rangeStartInternal.value = null
      isOpen.value = false
      emit('blur')
    }
  }
}

function adjustMonth(step: number) {
  const newDate = new Date(viewYear.value, viewMonth.value + step, 1)
  viewYear.value = newDate.getFullYear()
  viewMonth.value = newDate.getMonth()
}

function selectMonth(month: number) {
  viewMonth.value = month
  viewMode.value = 'days'
}

function selectYear(year: number) {
  viewYear.value = year
  viewMode.value = 'days'
}

function getCellClasses(cell: CalendarCell) {
  return {
    'other-month': !cell.isCurrentMonth,
    today: cell.isToday,
    selected: cell.isSelected,
    'in-range': cell.inRange,
    'range-start': cell.isRangeStart,
    'range-end': cell.isRangeEnd,
    disabled: cell.isDisabled,
  }
}

// UI Logic
function toggleOpen() {
  if (!props.disabled) {
    isOpen.value = !isOpen.value
    if (!isOpen.value) emit('blur')
  }
}

function handleOutsideClick(e: MouseEvent) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target as Node)) {
    if (isOpen.value) emit('blur')
    isOpen.value = false
  }
}

watch(isOpen, async (open) => {
  if (open) {
    const initial = (props.range ? props.modelValue?.start : props.modelValue) || new Date()
    viewYear.value = (initial as Date).getFullYear()
    viewMonth.value = (initial as Date).getMonth()
    viewMode.value = 'days'

    await nextTick()
    calculateDropdownPosition()
    dropdownRef.value?.focus()
  } else {
    rangeStartInternal.value = null
  }
})

onMounted(() => document.addEventListener('mousedown', handleOutsideClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', handleOutsideClick))
</script>

<style scoped>
.datepicker-wrapper {
  position: relative;
  display: inline-block;
  min-width: 220px;
}

.datepicker-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: inherit;
  text-align: left;
}

.datepicker-trigger.invalid {
  border-color: var(--destructive);
  background: color-mix(in srgb, var(--destructive) 10%, transparent) !important;
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--destructive) 12%, transparent);
}

.datepicker-icon {
  flex-shrink: 0;
  color: color-mix(in srgb, var(--foreground) 42%, transparent);
}

.datepicker-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.datepicker-chevron {
  flex-shrink: 0;
  color: color-mix(in srgb, var(--foreground) 42%, transparent);
  transition: transform 0.2s ease;
}

.datepicker-wrapper.open .datepicker-chevron {
  transform: rotate(180deg);
}

.datepicker-dropdown {
  position: absolute;
  left: 0;
  z-index: 50;
  width: 280px;
  background: var(--popover);
  color: var(--foreground);
  border: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgb(0 0 0 / 11%);
  overflow: hidden;
  padding: 0.5rem;
  outline: none;
}

.datepicker-dropdown.bottom {
  top: calc(100% + 4px);
}

.datepicker-dropdown.top {
  bottom: calc(100% + 4px);
}

.dp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.15rem 0.1rem 0.5rem;
  gap: 0.25rem;
}

.dp-header-center {
  display: flex;
  gap: 0.2rem;
  align-items: center;
}

.dp-nav-btn,
.dp-month-btn,
.dp-year-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  border-radius: 7px;
  transition: background 0.12s ease;
  font: inherit;
}

.dp-nav-btn {
  width: 28px;
  height: 28px;
  padding: 0;
  flex-shrink: 0;
}

.dp-nav-btn:hover {
  background: color-mix(in srgb, var(--foreground) 10%, transparent);
}

.dp-month-btn,
.dp-year-btn {
  padding: 0.2rem 0.45rem;
  font-size: 0.875rem;
  font-weight: 600;
  height: 28px;
}

.dp-month-btn:hover,
.dp-year-btn:hover {
  background: color-mix(in srgb, var(--foreground) 10%, transparent);
}

.dp-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 0.2rem;
}

.dp-weekday {
  text-align: center;
  font-size: 0.7rem;
  font-weight: 500;
  color: color-mix(in srgb, var(--foreground) 42%, transparent);
  padding: 0.2rem 0;
}

.dp-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
}

.dp-day {
  padding: 0;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  aspect-ratio: 1;
  font-size: 0.8125rem;
  background: none;
  border: none;
  border-radius: 7px;
  cursor: pointer;
  color: inherit;
  font: inherit;
  transition:
    background 0.1s ease,
    color 0.1s ease;
  z-index: 1;
}

.dp-day:focus-visible {
  box-shadow: 0 0 0 2px var(--primary);
}

.dp-day:hover:not(.selected):not(:disabled) {
  background: color-mix(in srgb, var(--foreground) 10%, transparent);
}

.dp-day.other-month {
  color: color-mix(in srgb, var(--foreground) 30%, transparent);
}

.dp-day.today:not(.selected) {
  font-weight: 700;
  color: var(--primary);
}

.dp-day.today:not(.selected)::after {
  content: '';
  position: absolute;
  bottom: 3px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--primary);
}

.dp-day.selected {
  background: var(--primary);
  color: var(--primary-foreground, #fff);
  font-weight: 600;
  border-radius: 7px;
}

.dp-day.in-range {
  background: color-mix(in srgb, var(--primary) 12%, transparent);
  border-radius: 0;
}

.dp-day.range-start {
  background: var(--primary);
  color: var(--primary-foreground, #fff);
  font-weight: 600;
  border-radius: 7px 0 0 7px;
}

.dp-day.range-end {
  background: var(--primary);
  color: var(--primary-foreground, #fff);
  font-weight: 600;
  border-radius: 0 7px 7px 0;
}

.dp-day.range-start.range-end {
  border-radius: 7px;
}

.dp-day:disabled,
.dp-day.disabled {
  opacity: 0.35;
  cursor: not-allowed;
  pointer-events: none;
}

.dp-month-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4px;
  padding: 0.25rem 0;
}

.dp-month-item {
  padding: 0.5rem 0.25rem;
  background: none;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  color: inherit;
  font: inherit;
  font-size: 0.8125rem;
  text-align: center;
  transition: background 0.1s ease;
}

.dp-month-item:hover:not(.selected) {
  background: color-mix(in srgb, var(--foreground) 10%, transparent);
}

.dp-month-item.today {
  color: var(--primary);
  font-weight: 600;
}

.dp-month-item.selected {
  background: var(--primary);
  color: var(--primary-foreground, #fff);
  font-weight: 600;
}

.dp-year-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4px;
  padding: 0.25rem 0;
  max-height: 200px;
  overflow-y: auto;
}

.dp-year-item {
  padding: 0.5rem 0.25rem;
  background: none;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  color: inherit;
  font: inherit;
  font-size: 0.8125rem;
  text-align: center;
  transition: background 0.1s ease;
}

.dp-year-item:hover:not(.selected) {
  background: color-mix(in srgb, var(--foreground) 10%, transparent);
}

.dp-year-item.today {
  color: var(--primary);
  font-weight: 600;
}

.dp-year-item.selected {
  background: var(--primary);
  color: var(--primary-foreground, #fff);
  font-weight: 600;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>
