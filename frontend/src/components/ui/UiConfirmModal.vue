<template>
  <ui-modal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :max-width="maxWidth"
  >
    <template #title v-if="title">
      <h3 class="confirm-modal-title">{{ title }}</h3>
    </template>

    <p v-if="message">{{ message }}</p>

    <div class="confirm-modal-content">
      <slot />
    </div>

    <template #footer>
      <div class="confirm-modal-actions">
        <ui-button size="sm" variant="secondary" @click="cancel">{{ cancelText }}</ui-button>
        <ui-button size="sm" :variant="confirmVariant" @click="confirm" :disabled="loading">{{
          confirmText
        }}</ui-button>
      </div>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiModal from './UiModal.vue'
import UiButton from './UiButton.vue'

interface Props {
  modelValue: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  confirmVariant?: 'default' | 'danger' | 'secondary'
  loading?: boolean
  maxWidth?: string
}

withDefaults(defineProps<Props>(), {
  title: 'Confirm Action',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  confirmVariant: 'default',
  loading: false,
  maxWidth: '400px',
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const cancel = () => {
  emit('update:modelValue', false)
  emit('cancel')
}

const confirm = () => {
  emit('confirm')
}
</script>

<style scoped>
.confirm-modal-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--foreground);
}

.confirm-modal-content p {
  color: var(--muted-foreground);
  line-height: 1.5;
}

.confirm-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  width: 100%;
}
</style>
