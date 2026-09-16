<template>
  <DateFieldRoot
    v-model="dateValue"
    v-bind="$attrs"
    class="datepicker-wrapper"
    locale="uk-UA"
    :disabled="disabled"
    :required="required"
    :invalid="!!props.isInvalid"
    :min-value="minValue"
    :max-value="maxValue"
    :placeholder="placeholderValue"
    @update:model-value="handleValueChange"
    @blur="emit('blur')"
  >
    <template #default="{ segments }">
      <div
        :class="['datepicker-field', { invalid: !!props.isInvalid }]"
        :aria-invalid="props.isInvalid ? 'true' : 'false'"
      >
        <template v-for="segment in segments" :key="segment.part">
          <DateFieldInput :part="segment.part" class="datepicker-segment">
            {{ segment.value }}
          </DateFieldInput>
        </template>
      </div>
    </template>
  </DateFieldRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DateFieldInput, DateFieldRoot } from 'reka-ui'
import { CalendarDate, type DateValue, fromDate } from '@internationalized/date'

type Props = {
  modelValue?: Date | null
  placeholder?: string
  disabled?: boolean
  required?: boolean
  minDate?: Date
  maxDate?: Date
  isInvalid?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Pick a date',
  disabled: false,
  required: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: Date | null): void
  (e: 'blur'): void
}>()

const toCalendarDate = (date: Date) => {
  const value = fromDate(date, 'UTC')
  return new CalendarDate(value.year, value.month, value.day)
}

const toNativeDate = (value: DateValue) => value.toDate('UTC')

const minValue = computed(() => (props.minDate ? toCalendarDate(props.minDate) : undefined))
const maxValue = computed(() => (props.maxDate ? toCalendarDate(props.maxDate) : undefined))

const dateValue = computed<DateValue | undefined>({
  get: () => (props.modelValue ? toCalendarDate(props.modelValue) : undefined),
  set: (value) => handleValueChange(value),
})

const placeholderValue = computed(() => toCalendarDate(props.modelValue || new Date()))

function handleValueChange(value: DateValue | undefined) {
  emit('update:modelValue', value ? toNativeDate(value) : null)
}
</script>

<style scoped>
:deep(.datepicker-wrapper) {
  display: flex;
  align-items: center;
  width: 100%;
}

.datepicker-field {
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

.datepicker-field:focus-within {
  outline: 2px solid color-mix(in srgb, var(--primary) 35%, transparent);
  outline-offset: 1px;
}

.datepicker-field.invalid {
  border-color: var(--destructive);
}

.datepicker-field[data-disabled] {
  cursor: not-allowed;
  opacity: 0.55;
}

:deep(.datepicker-segment) {
  color: inherit;
}

:deep(.datepicker-field [data-placeholder]) {
  color: color-mix(in srgb, var(--foreground) 42%, transparent);
}
</style>
