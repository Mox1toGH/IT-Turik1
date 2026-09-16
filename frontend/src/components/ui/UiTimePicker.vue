<template>
  <TimeFieldRoot
    v-model="timeValue"
    v-bind="$attrs"
    class="time-wrapper"
    locale="uk-UA"
    :hour-cycle="24"
    granularity="minute"
    :disabled="props.disabled"
    :required="props.required"
    :invalid="props.isInvalid"
    :placeholder="placeholderValue"
    @update:model-value="handleTimeChange"
    @blur="emit('blur')"
  >
    <template #default="{ segments }">
      <div
        :class="['time-field', { invalid: props.isInvalid }]"
        :aria-invalid="props.isInvalid || undefined"
      >
        <template v-for="segment in segments" :key="segment.part">
          <TimeFieldInput :part="segment.part" class="time-segment">
            {{ segment.value }}
          </TimeFieldInput>
        </template>
      </div>
    </template>
  </TimeFieldRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { TimeFieldInput, TimeFieldRoot } from 'reka-ui'
import { Time } from '@internationalized/date'

interface TimeLike {
  hour: number
  minute: number
}

interface Props {
  modelValue: string
  isInvalid?: boolean
  disabled?: boolean
  required?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isInvalid: false,
  disabled: false,
  required: false,
})

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
  (event: 'blur'): void
}>()

const parseTime = (value: string) => {
  const [hours = '0', minutes = '0'] = value.split(':')
  return new Time(Number(hours) || 0, Number(minutes) || 0)
}

const formatTime = (value: TimeLike) =>
  `${value.hour.toString().padStart(2, '0')}:${value.minute.toString().padStart(2, '0')}`

const timeValue = computed<Time | undefined>({
  get: () => (props.modelValue ? parseTime(props.modelValue) : undefined),
  set: (value) => handleTimeChange(value),
})

const placeholderValue = computed(() => parseTime(props.modelValue || '00:00'))

function handleTimeChange(value: TimeLike | undefined) {
  if (value) emit('update:modelValue', formatTime(value))
}
</script>

<style scoped>
.time-wrapper {
  display: block;
  width: 100%;
}

.time-field {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  width: 100%;
  min-height: 2.5rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid color-mix(in srgb, var(--border) 60%, transparent);
  border-radius: 8px;
  background: transparent;
  color: inherit;
  font: inherit;
  cursor: text;
}

.time-field:focus-within {
  outline: 2px solid color-mix(in srgb, var(--primary) 35%, transparent);
  outline-offset: 1px;
}

.time-field.invalid {
  border-color: var(--destructive);
}

.time-field[data-disabled] {
  cursor: not-allowed;
  opacity: 0.55;
}

.time-segment {
  color: inherit;
}

:deep(.time-field [data-placeholder]) {
  color: color-mix(in srgb, var(--foreground) 42%, transparent);
}
</style>
