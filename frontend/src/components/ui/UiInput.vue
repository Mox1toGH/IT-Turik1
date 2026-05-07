<template>
  <div v-if="type === 'number'" :class="['number-wrapper', { invalid: isInvalid }]">
    <button
      class="stepper-btn"
      type="button"
      @click="decrement"
      :disabled="isAtMin"
      aria-label="Decrement"
    >
      -
    </button>

    <input
      v-bind="$attrs"
      class="number-input"
      type="text"
      inputmode="numeric"
      :value="modelValue"
      @input="handleInput"
      @keydown="handleKeydown"
    />

    <button
      class="stepper-btn"
      type="button"
      @click="increment"
      :disabled="isAtMax"
      aria-label="Increment"
    >
      +
    </button>
  </div>

  <input
    v-else
    :class="['input', { invalid: isInvalid }]"
    :type="type"
    :value="modelValue"
    @input="handleInput"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue?: string | number
  isInvalid?: boolean
  type?: string
  min?: string | number
  max?: string | number
  step?: number
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  isInvalid: false,
  type: 'text',
  step: 1,
})

const emit = defineEmits(['update:modelValue'])

const numericValue = computed(() => Number(props.modelValue) || 0)

const isAtMin = computed(() => props.min !== undefined && numericValue.value <= Number(props.min))
const isAtMax = computed(() => props.max !== undefined && numericValue.value >= Number(props.max))

function clamp(value: number): number {
  let v = value
  if (props.min !== undefined) v = Math.max(Number(props.min), v)
  if (props.max !== undefined) v = Math.min(Number(props.max), v)
  return v
}

function increment() {
  emit('update:modelValue', clamp(numericValue.value + props.step))
}

function decrement() {
  emit('update:modelValue', clamp(numericValue.value - props.step))
}

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  const raw = target.value

  if (props.type === 'number') {
    if (raw === '' || raw === '-') {
      emit('update:modelValue', raw)
      return
    }

    const parsed = Number(raw)
    if (isNaN(parsed)) {
      target.value = String(props.min)
      emit('update:modelValue', props.min)
      return
    }

    const clamped = clamp(parsed)
    target.value = String(clamped)
    emit('update:modelValue', clamped)
  } else {
    emit('update:modelValue', target.value)
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'ArrowUp') {
    event.preventDefault()
    increment()
  }
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    decrement()
  }
}
</script>

<style scoped>
.input {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.75rem 0.85rem;
  font: inherit;
  background: var(--input);
  color: var(--foreground);
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.input:focus {
  outline: none;
  box-shadow: 0 0 0 3px var(--ring);
}

.input:disabled {
  cursor: not-allowed;
}

.input[type='radio']:focus {
  box-shadow: none;
}

.invalid {
  border-color: var(--destructive);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--destructive) 12%, transparent);
}

.number-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 0;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--input);
  overflow: hidden;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.number-wrapper:focus-within {
  box-shadow: 0 0 0 3px var(--ring);
}

.number-wrapper.invalid {
  border-color: var(--destructive);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--destructive) 12%, transparent);
}

.number-input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--foreground);
  font: inherit;
  padding: 0.75rem 0;
  width: 5ch;
  text-align: center;
  outline: none;
}

.stepper-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 100%;
  padding: 0.75rem 0;
  min-height: 2.625rem;
  background: color-mix(in srgb, var(--foreground) 20%, transparent);
  border: none;
  color: var(--foreground);
  cursor: pointer;
  opacity: 0.5;
  transition:
    opacity 0.15s ease,
    background 0.15s ease;
  flex-shrink: 0;
}

.stepper-btn:disabled {
  opacity: 0.25;
  cursor: not-allowed;
}

.stepper-btn:first-child {
  border-right: 1px solid var(--border);
}

.stepper-btn:last-child {
  border-left: 1px solid var(--border);
}
</style>
