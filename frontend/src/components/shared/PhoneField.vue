<template>
  <div class="phone-field">
    <VueTelInput
      v-bind="$attrs"
      v-model="phoneUiValue"
      mode="international"
      :auto-default-country="true"
      :dropdown-options="{ showDialCodeInSelection: true, showSearchBox: true, showFlags: true }"
      :input-options="{ showDialCode: true, placeholder }"
      :valid-characters-only="true"
      :class="['phone-input', { invalid: props.isInvalid }]"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { VueTelInput } from 'vue-tel-input'

interface Props {
  modelValue?: string
  placeholder?: string
  isInvalid?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Enter phone number',
  isInvalid: false,
})

const emit = defineEmits(['update:modelValue'])
const phoneUiValue = ref(props.modelValue || '')

const normalizePhoneNumber = (value: string) => {
  if (!value) {
    return ''
  }

  const hasPlus = value.trim().startsWith('+')
  const digitsOnly = value.replace(/[^\d]/g, '')
  if (!digitsOnly) {
    return ''
  }

  return hasPlus ? `+${digitsOnly}` : digitsOnly
}

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== phoneUiValue.value) {
      phoneUiValue.value = newValue || ''
    }
  },
)

watch(phoneUiValue, (newValue) => {
  emit('update:modelValue', normalizePhoneNumber(newValue))
})
</script>

<style scoped>
.phone-field {
  display: grid;
  gap: 0.35rem;
}

.phone-input {
  border-radius: 10px;
  width: 100%;
  background: var(--input);
  border-color: var(--border);
  color: var(--foreground) !important;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.phone-input:focus-within {
  outline: none;
  border-color: transparent;
  box-shadow: 0 0 0 3px var(--ring);
}

.phone-input.invalid {
  border-color: var(--destructive);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--destructive) 12%, transparent);
}

:deep(.vti) {
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--input);
  box-shadow: none;
}

:deep(.vti__dropdown:hover) {
  background-color: inherit;
  border-radius: 12px;
}

:deep(.vti__dropdown-list) {
  background: var(--popover) !important;
  border-color: var(--border);
}

:deep(.vti__search_box_container) {
  padding: 0.5rem;
}

:deep(.vti__input) {
  font: inherit;
  padding: 0.75rem 0.85rem;
  border-radius: 10px;
  background: var(--input);
  color: var(--foreground);
  width: 100%;
}

:deep(.vti__dropdown-item.highlighted) {
  background-color: var(--muted);
}

:deep(.vti:focus-within) {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--ring);
}
</style>
