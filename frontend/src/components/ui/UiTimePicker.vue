<template>
  <div class="time-wrapper" ref="wrapperRef">
    <input
      v-bind="$attrs"
      ref="inputRef"
      type="text"
      inputmode="numeric"
      class="input"
      :class="{ invalid: isInvalid }"
      :value="modelValue"
      :aria-invalid="isInvalid || undefined"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
      placeholder="00:00"
      maxlength="5"
      autocomplete="off"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
      @keydown="handleKeyDown"
    />

    <Transition name="dropdown">
      <div
        v-if="isOpen"
        ref="dropdownRef"
        :class="['dropdown', dropdownPosition]"
        role="dialog"
        @mousedown.prevent
      >
        <div class="col" role="listbox" aria-label="Hours">
          <div
            v-for="h in hours"
            :key="h"
            :ref="
              (el) => {
                if (h === selectedHour) activeHourRef = el as HTMLElement
              }
            "
            role="option"
            class="col-item"
            :class="{
              active: h === selectedHour,
              'kb-focus': currentFocusCol === 'hours' && h === selectedHour,
            }"
            :aria-selected="h === selectedHour"
            @click="selectHour(h)"
          >
            {{ h.toString().padStart(2, '0') }}
          </div>
        </div>

        <span class="sep" aria-hidden="true">:</span>

        <div class="col" role="listbox" aria-label="Minutes">
          <div
            v-for="m in minutes"
            :key="m"
            :ref="
              (el) => {
                if (m === selectedMinute) activeMinuteRef = el as HTMLElement
              }
            "
            role="option"
            class="col-item"
            :class="{
              active: m === selectedMinute,
              'kb-focus': currentFocusCol === 'minutes' && m === selectedMinute,
            }"
            :aria-selected="m === selectedMinute"
            @click="selectMinute(m)"
          >
            {{ m.toString().padStart(2, '0') }}
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'

interface Props {
  modelValue: string
  isInvalid?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const wrapperRef = ref<HTMLElement | null>(null)
const dropdownRef = ref<HTMLElement | null>(null)
const activeHourRef = ref<HTMLElement | null>(null)
const activeMinuteRef = ref<HTMLElement | null>(null)

const isOpen = ref(false)
const dropdownPosition = ref<'bottom' | 'top'>('bottom')
const currentFocusCol = ref<'hours' | 'minutes'>('hours')

const hours = Array.from({ length: 24 }, (_, i) => i)
const minutes = Array.from({ length: 60 }, (_, i) => i)

const selectedHour = computed(() => {
  const [h] = props.modelValue.split(':')
  const parsed = parseInt(h ?? '0')
  return isNaN(parsed) ? 0 : parsed
})

const selectedMinute = computed(() => {
  const [, m] = props.modelValue.split(':')
  const parsed = parseInt(m ?? '0')
  return isNaN(parsed) ? 0 : parsed
})

function updateValue(h: number, m: number) {
  const time = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`
  emit('update:modelValue', time)
}

function calculatePosition() {
  if (!wrapperRef.value || !dropdownRef.value) return
  const rect = wrapperRef.value.getBoundingClientRect()
  const dropdownHeight = 210 // max-height + padding
  const spaceBelow = window.innerHeight - rect.bottom
  dropdownPosition.value = spaceBelow < dropdownHeight ? 'top' : 'bottom'
}

function scrollToActive() {
  activeHourRef.value?.scrollIntoView({ block: 'nearest' })
  activeMinuteRef.value?.scrollIntoView({ block: 'nearest' })
}

function handleKeyDown(e: KeyboardEvent) {
  if (!isOpen.value) {
    if (e.key === 'ArrowDown' || e.key === 'Enter') isOpen.value = true
    return
  }

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      currentFocusCol.value === 'hours'
        ? updateValue((selectedHour.value + 1) % 24, selectedMinute.value)
        : updateValue(selectedHour.value, (selectedMinute.value + 1) % 60)
      break
    case 'ArrowUp':
      e.preventDefault()
      currentFocusCol.value === 'hours'
        ? updateValue((selectedHour.value - 1 + 24) % 24, selectedMinute.value)
        : updateValue(selectedHour.value, (selectedMinute.value - 1 + 60) % 60)
      break
    case 'ArrowRight':
    case 'ArrowLeft':
      e.preventDefault()
      currentFocusCol.value = currentFocusCol.value === 'hours' ? 'minutes' : 'hours'
      break
    case 'Enter':
    case 'Escape':
      e.preventDefault()
      isOpen.value = false
      break
  }
}

function handleInput(event: Event) {
  const input = event.target as HTMLInputElement
  let val = input.value.replace(/\D/g, '').slice(0, 4)

  if (val.length >= 2) {
    let hour = parseInt(val.slice(0, 2))
    if (hour > 23) hour = 23
    val = hour.toString().padStart(2, '0') + val.slice(2)
  }

  if (val.length >= 4) {
    const hoursPart = val.slice(0, 2)
    let minutesPart = val.slice(2)

    if (minutesPart.length >= 2) {
      let minute = parseInt(minutesPart.slice(0, 2))
      if (minute > 59) minute = 59
      minutesPart = minute.toString().padStart(2, '0')
    }

    val = hoursPart + ':' + minutesPart
  }

  if (input.value !== val) {
    input.value = val
  }

  emit('update:modelValue', val)
}

function handleFocus() {
  isOpen.value = true
}

function handleBlur() {
  isOpen.value = false
  const h = selectedHour.value.toString().padStart(2, '0')
  const m = selectedMinute.value.toString().padStart(2, '0')
  emit('update:modelValue', `${h}:${m}`)
}

function selectHour(hour: number) {
  updateValue(hour, selectedMinute.value)
  currentFocusCol.value = 'hours'
}

function selectMinute(minute: number) {
  updateValue(selectedHour.value, minute)
  currentFocusCol.value = 'minutes'
}

watch(isOpen, async (val) => {
  if (val) {
    await nextTick()
    calculatePosition()
    scrollToActive()
  }
})

watch([selectedHour, selectedMinute], () => {
  if (isOpen.value) nextTick(scrollToActive)
})
</script>

<style scoped>
.time-wrapper {
  position: relative;
  display: inline-block;
}

.input {
  width: 100%;
  padding: 0.75rem;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
  background: var(--input);
  color: var(--foreground);
  text-align: center;
  font-variant-numeric: tabular-nums;
  transition: all 0.2s;
}

.invalid {
  border-color: var(--destructive);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--destructive) 12%, transparent);
}

.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 20%, transparent);
}

.dropdown {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  background: var(--popover);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 8px;
  display: flex;
  gap: 4px;
  z-index: 100;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.dropdown.bottom {
  top: calc(100% + 8px);
}
.dropdown.top {
  bottom: calc(100% + 8px);
}

.col {
  display: flex;
  flex-direction: column;
  max-height: 180px;
  overflow-y: auto;
  scrollbar-width: none;
  scroll-behavior: smooth;
}

.col::-webkit-scrollbar {
  display: none;
}

.col-item {
  width: 42px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: 0.1s;
}

.col-item:hover {
  background: color-mix(in srgb, var(--primary) 20%, transparent);
}
.col-item.active {
  background: var(--primary);
  color: var(--primary-foreground);
}

.sep {
  align-self: center;
  font-weight: bold;
  opacity: 0.5;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition:
    opacity 0.2s,
    transform 0.2s;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(5px);
}
</style>
