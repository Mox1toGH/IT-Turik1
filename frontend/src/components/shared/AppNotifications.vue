<template>
  <Transition name="global-notice" mode="out-in">
    <div
      v-if="notification"
      :key="notification.id"
      :class="['notice', 'app-notice', notification.type, `type-${notification.type}`]"
      role="status"
      aria-live="polite"
    >
      <div class="notification-info">
        <div v-if="notification.type === 'success'" class="notif-icon notif-icon--success">
          <SelectedIcon />
        </div>
        <div v-if="notification.type === 'error'" class="notif-icon notif-icon--error">
          <CrossIcon />
        </div>
        <span class="notification-text">{{ notification.message }}</span>
      </div>

      <ui-button
        class="close-notice-btn"
        variant="secondary"
        size="sm"
        type="button"
        @click="hideNotification()"
        ><CrossIcon
      /></ui-button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { useNotification } from '@/composables/useNotification'
import UiButton from '../ui/UiButton.vue'
import SelectedIcon from '@/icons/SelectedIcon.vue'
import CrossIcon from '@/icons/CrossIcon.vue'

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
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.24);
  color: var(--foreground);
  backdrop-filter: blur(20px);
  background: var(--background);
  border: 1px solid var(--border);
}

.notification-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.notification-info {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.notif-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.notif-icon--success {
  background: color-mix(in srgb, var(--primary) 20%, transparent);
  color: var(--primary);
}

.notif-icon--error {
  background: color-mix(in srgb, var(--destructive) 20%, transparent);
  color: var(--destructive);
}

.notification-text {
  word-break: break-word;
}

.close-notice-btn {
  background: transparent;
  border: none;
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
</style>
