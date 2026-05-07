<template>
  <div class="password-field">
    <ui-input
      v-bind="$attrs"
      :is-invalid="props.isInvalid"
      :type="isVisible ? 'text' : 'password'"
      :value="modelValue"
      :disabled="disabled"
      class="password-input"
      @input="onInput"
    />

    <button
      :aria-label="isVisible ? 'Hide password' : 'Show password'"
      :aria-pressed="isVisible"
      :disabled="disabled"
      type="button"
      :class="['password-toggle', { invalid: isInvalid }]"
    >
      <EyeIcon class="toggle-icon" @click="isVisible = !isVisible" :is-crossed="!isVisible" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UiInput from './UiInput.vue'
import EyeIcon from '@/icons/EyeIcon.vue'

interface Props {
  modelValue: string
  isInvalid?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  invalid: false,
  disabled: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const isVisible = ref(false)

const onInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<style scoped>
.password-field {
  position: relative;
}

.password-input {
  width: 100%;
  padding-right: 2.8rem;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
}

.password-toggle.invalid {
  color: var(--destructive);
}

.password-toggle.is-invalid .eye-icon {
  color: var(--destructive) !important;
}

.password-toggle:disabled {
  cursor: not-allowed;
}

.toggle-icon {
  width: 1.05rem;
  height: 1.05rem;
}
</style>
