<template>
  <textarea
    :class="['textarea', { invalid: props.isInvalid }]"
    :value="props.modelValue"
    :placeholder="props.placeholder"
    rows="1"
    @input="handleInput"
  />
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string
  isInvalid?: boolean
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  isInvalid: false,
  placeholder: '',
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
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 0.55rem 0.7rem;
  font: inherit;
  font-size: 0.84rem;
  line-height: 1.5;
  background: var(--input);
  color: var(--foreground);
  resize: vertical;
  min-height: 64px;
  display: block;

  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.textarea:focus {
  outline: none;
  border-color: var(--ring);
  box-shadow: 0 0 0 2px var(--ring);
}

.textarea:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  background: var(--subtle);
}

.textarea.invalid {
  border-color: var(--destructive);
  box-shadow: 0 0 0 3px var(--destructive-soft);
}

.textarea::placeholder {
  color: var(--placeholder);
}
</style>
