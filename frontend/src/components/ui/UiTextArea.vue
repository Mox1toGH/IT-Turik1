<template>
  <textarea
    :class="['textarea', { invalid: props.isInvalid }]"
    :value="props.modelValue"
    rows="1"
    @input="handleInput"
  />
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string
  isInvalid?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  isInvalid: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  if (target) {
    emit('update:modelValue', target.value)
  }
}
</script>

<style scoped>
.textarea {
  width: 100%;
  border: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
  border-radius: 12px;
  padding: 0.75rem 0.85rem;
  font: inherit;
  line-height: 1.5;
  background: var(--input);
  color: var(--foreground);
  resize: vertical;
  min-height: 80px;
  display: block;

  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.textarea:focus {
  outline: none;
  border-color: var(--ring);
  box-shadow: 0 0 0 3px var(--ring);
}

.textarea:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  background: color-mix(in srgb, var(--input) 80%, var(--muted));
}

.invalid {
  border-color: var(--destructive);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--destructive) 12%, transparent);
}

.textarea::placeholder {
  color: color-mix(in srgb, var(--foreground) 40%, transparent);
}
</style>
