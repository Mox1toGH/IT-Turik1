<template>
  <input
    v-bind="$attrs"
    type="tel"
    inputmode="tel"
    autocomplete="tel"
    :value="modelValue"
    :placeholder="placeholder"
    :class="['phone-input', { invalid: isInvalid }]"
    @input="handleInput"
  />
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string
  placeholder?: string
  isInvalid?: boolean
}

withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '+380 00 000 00 00',
  isInvalid: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

function handleInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  const digits = value.replace(/\D/g, '')
  emit('update:modelValue', value.trim().startsWith('+') ? `+${digits}` : digits)
}
</script>

<style scoped>
.phone-input {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.45rem 0.7rem;
  font: inherit;
  font-size: 0.84rem;
  background: var(--input);
  color: var(--foreground);
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.phone-input:focus {
  outline: none;
  border-color: transparent;
  box-shadow: 0 0 0 3px var(--ring);
}

.phone-input:disabled {
  cursor: not-allowed;
}

.phone-input.invalid {
  border-color: var(--destructive);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--destructive) 12%, transparent);
}
</style>
