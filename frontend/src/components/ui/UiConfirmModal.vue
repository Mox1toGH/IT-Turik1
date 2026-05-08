<template>
  <ui-modal :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" :max-width="maxWidth">
    <template #title v-if="title">
      <h3 class="confirm-modal-title">{{ title }}</h3>
    </template>

    <div class="confirm-modal-content">
      <p>{{ message }}</p>
    </div>

    <template #footer>
      <div class="confirm-modal-actions">
        <ui-button variant="secondary" @click="cancel">{{ cancelText }}</ui-button>
        <ui-button :variant="confirmVariant" @click="confirm" :disabled="loading">{{ confirmText }}</ui-button>
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
  message: string
  confirmText?: string
  cancelText?: string
  confirmVariant?: 'primary' | 'danger' | 'secondary'
  loading?: boolean
  maxWidth?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Confirm Action',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  confirmVariant: 'primary',
  loading: false,
  maxWidth: '400px'
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
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--foreground);
}

.confirm-modal-content {
  padding: 0.5rem 0;
}

.confirm-modal-content p {
  margin: 0;
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
