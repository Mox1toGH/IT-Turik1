<template>
  <div :class="['number-wrapper', { invalid: isInvalid }]">
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
      :disabled="disabled"
      :required="required"
      :aria-invalid="isInvalid || undefined"
      @input="handleInput"
      @keydown="handleKeydown"
    />

    <button
      class="stepper-btn"
      type="button"
      @click="increment"
      :disabled="isAtMax || disabled"
      aria-label="Increment"
    >
      +
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

defineOptions({ inheritAttrs: false })

interface Props {
  modelValue?: string | number
  isInvalid?: boolean
  min?: string | number
  max?: string | number
  step?: number
  disabled?: boolean
  required?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  isInvalid: false,
  step: 1,
  disabled: false,
  required: false,
})

const emit = defineEmits<{
  (event: 'update:modelValue', value: string | number): void
}>()

const numericValue = computed(() => Number(props.modelValue) || 0)
const isAtMin = computed(
  () => props.disabled || (props.min !== undefined && numericValue.value <= Number(props.min)),
)
const isAtMax = computed(
  () => props.disabled || (props.max !== undefined && numericValue.value >= Number(props.max)),
)

function clamp(value: number): number {
  let result = value
  if (props.min !== undefined) result = Math.max(Number(props.min), result)
  if (props.max !== undefined) result = Math.min(Number(props.max), result)
  return result
}

function updateValue(value: number) {
  emit('update:modelValue', clamp(value))
}

function increment() {
  updateValue(numericValue.value + props.step)
}

function decrement() {
  updateValue(numericValue.value - props.step)
}

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  const raw = target.value

  if (raw === '' || raw === '-') {
    emit('update:modelValue', raw)
    return
  }

  const parsed = Number(raw)
  if (Number.isNaN(parsed)) {
    const fallback = props.min ?? ''
    target.value = String(fallback)
    emit('update:modelValue', fallback)
    return
  }

  const clamped = clamp(parsed)
  target.value = String(clamped)
  emit('update:modelValue', clamped)
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
.number-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 0;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--input);
  overflow: hidden;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.number-wrapper:focus-within {
  box-shadow: 0 0 0 2px var(--ring);
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
  padding: 0.3rem 0;
  font-size: 0.84rem;
  width: 5ch;
  text-align: center;
  outline: none;
}

.number-input:disabled {
  cursor: not-allowed;
}

.stepper-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.9rem;
  height: 100%;
  padding: 0.4rem 0;
  min-height: 2.25rem;
  background: color-mix(in srgb, var(--foreground) 14%, transparent);
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
  background: color-mix(in srgb, var(--foreground) 0.1%, transparent);
  cursor: not-allowed;
}

.stepper-btn:first-child {
  border-right: 1px solid var(--border);
}

.stepper-btn:last-child {
  border-left: 1px solid var(--border);
}
</style>
