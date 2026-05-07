<template>
  <button
    type="button"
    class="visibility-switch"
    role="switch"
    :aria-checked="modelValue"
    :class="{ 'is-checked': modelValue }"
    @click="toggleVisibility"
    @keydown="onVisibilityKeydown"
  >
    <span class="switch-knob" />
  </button>
</template>

<script setup lang="ts">
interface Props {
  modelValue?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const toggleVisibility = () => {
  emit('update:modelValue', !props.modelValue)
}

const onVisibilityKeydown = (event: KeyboardEvent) => {
  if (event.key === 'ArrowLeft') {
    event.preventDefault()
    emit('update:modelValue', false)
    return
  }

  if (event.key === 'ArrowRight') {
    event.preventDefault()
    emit('update:modelValue', true)
    return
  }

  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    toggleVisibility()
  }
}
</script>

<style>
.visibility-switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  width: 3rem;
  height: 1.7rem;
  padding: 0.17rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: color-mix(in srgb, var(--foreground) 15%, transparent);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 180ms ease;
}

.visibility-switch:focus-visible {
  outline: 2px solid var(--brand-500);
  outline-offset: 2px;
}

.visibility-switch.is-checked {
  background: var(--brand-500);
  border-color: var(--brand-500);
}

.switch-knob {
  width: 1.2rem;
  height: 1.2rem;
  border-radius: 999px;
  border: 1px solid var(white);
  background: white;
  transform: translateX(0);
  transition: transform 180ms ease;
}

.visibility-switch.is-checked .switch-knob {
  transform: translateX(1.3rem);
  border-color: transparent;
  background: #fff;
}
</style>
