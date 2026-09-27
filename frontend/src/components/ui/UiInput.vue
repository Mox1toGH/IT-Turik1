<template>
  <input
    v-bind="$attrs"
    :class="['input', { invalid: isInvalid }]"
    :type="type"
    :value="modelValue"
    @input="handleInput"
  />
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string | number
  isInvalid?: boolean
  type?: string
}

withDefaults(defineProps<Props>(), {
  modelValue: '',
  isInvalid: false,
  type: 'text',
})

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
}>()

function handleInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>

<style scoped>
.input {
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

.input:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--ring);
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
</style>
