<template>
  <Transition name="global-notice" mode="out-in">
    <div
      v-if="notification"
      :key="notification.id"
      :class="['notice', 'app-notice', notification.type, `type-${notification.type}`]"
      role="status"
      aria-live="polite"
    >
      <span>{{ notification.message }}</span>
      <ui-button
        class="close-notice-btn"
        :variant="notification.type === 'success' ? 'default' : 'danger'"
        size="sm"
        type="button"
        @click="hideNotification()"
        ><X :size="16"
      /></ui-button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { useNotification } from '@/composables/useNotification'
import UiButton from '@/components/ui/UiButton'

const { notification, hideNotification } = useNotification()
</script>

<style scoped>
.app-notice {
  position: fixed;
  top: 1rem;
  right: 1rem;
  margin: 0;
  width: min(92vw, 420px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  z-index: 2000;
  box-shadow: var(--shadow-overlay);
  backdrop-filter: blur(20px);
}

.close-notice-btn {
  background: transparent;
  border: none;
}

.type-info {
  color: var(--foreground);
  background: var(--card);
  border-color: var(--border);
}

.type-warning {
  color: var(--foreground);
  background: color-mix(in srgb, var(--warning) 10%, var(--card));
  border-color: color-mix(in srgb, var(--warning) 45%, transparent);
}

.global-notice-enter-active,
.global-notice-leave-active {
  transition:
    opacity 220ms ease,
    transform 220ms ease;
}

.global-notice-enter-from,
.global-notice-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.global-notice-enter-to,
.global-notice-leave-from {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 680px) {
  .app-notice {
    top: 0.75rem;
    left: 0.75rem;
    right: 0.75rem;
    width: auto;
  }
}
</style>
