<template>
  <Transition name="global-notice" mode="out-in">
    <div
      v-if="notification"
      :key="notification.id"
      :class="[
        'app-notice',
        notification.type,
        `type-${notification.type}`,
        { 'has-actions': notification.actions && notification.actions.length },
      ]"
      role="status"
      aria-live="polite"
    >
      <div class="notice-main">
        <component :is="iconComponent" :size="18" class="notice-icon" aria-hidden="true" />
        <div class="notice-text">
          <span>{{ notification.message }}</span>
        </div>
        <ui-button
          variant="ghost"
          size="sm"
          type="button"
          aria-label="Dismiss notification"
          class="notice-close"
          @click="hideNotification()"
        >
          <X :size="16" />
        </ui-button>
      </div>
      <div v-if="notification.actions && notification.actions.length" class="notice-footer">
        <div class="notice-actions">
          <ui-button
            v-for="(action, idx) in notification.actions"
            :key="idx"
            variant="ghost"
            size="xs"
            type="button"
            @click="() => handleAction(action)"
          >
            {{ action.label }}
          </ui-button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { AlertCircle, AlertTriangle, CheckCircle2, Info, X } from 'lucide-vue-next'
import { useNotification, type NotificationAction } from '@/composables/useNotification'
import UiButton from '@/components/ui/UiButton'

const { notification, hideNotification } = useNotification()

const iconComponent = computed(() => {
  const type = notification.value?.type
  if (type === 'success') return CheckCircle2
  if (type === 'error') return AlertCircle
  if (type === 'warning') return AlertTriangle
  return Info
})

function handleAction(action: NotificationAction) {
  const result = action.onClick()
  if (result && typeof result === 'object' && 'then' in result) {
    Promise.resolve(result).finally(() => hideNotification())
    return
  }
  hideNotification()
}
</script>

<style scoped>
.app-notice {
  position: fixed;
  top: 1rem;
  right: 1rem;
  margin: 0;
  width: min(92vw, 420px);
  display: flex;
  flex-direction: column;
  z-index: 2000;
  background: var(--card);
  color: var(--card-foreground);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  box-shadow:
    0 10px 40px -10px rgb(0 0 0 / 0.25),
    0 2px 10px -2px rgb(0 0 0 / 0.15);
  overflow: hidden;
}

.notice-main {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 0.85rem;
}

.app-notice:not(.has-actions) .notice-main {
  padding-bottom: 0.75rem;
}

.notice-icon {
  flex: 0 0 auto;
}

.notice-text {
  flex: 1 1 auto;
  min-width: 0;
}

.notice-text > span {
  display: block;
  font-size: 0.9rem;
  line-height: 1.4;
  word-break: break-word;
}

.notice-close {
  flex: 0 0 auto;
  margin: -0.25rem -0.35rem -0.25rem 0;
  color: var(--muted-foreground);
}

.notice-close:hover {
  color: var(--foreground);
}

.notice-footer {
  display: flex;
  width: 100%;
  padding: 0.5rem 0.85rem 0.7rem;
  border-top: 1px solid var(--border);
  background: color-mix(in srgb, var(--muted) 35%, transparent);
}

.notice-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  width: 100%;
}

.type-success .notice-icon,
.success .notice-icon {
  color: var(--success, #22c55e);
}

.type-error .notice-icon,
.error .notice-icon {
  color: var(--destructive);
}

.type-warning .notice-icon,
.warning .notice-icon {
  color: var(--warning, #f59e0b);
}

.type-info .notice-icon,
.info .notice-icon {
  color: var(--muted-foreground);
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
