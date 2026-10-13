<template>
  <ui-card
    v-if="layout === 'list'"
    :class="['notification-card', { 'notification-card--unread': !notification.is_read }]"
    @click="onListCardClick"
  >
    <div class="notification-card__body">
      <div class="notification-card__meta">
        <span class="notification-card__category">{{
          getNotificationCategory(notification.event_type)
        }}</span>
        <span class="notification-card__meta-sep" aria-hidden="true">·</span>
        <time class="notification-card__date">{{
          formatNotificationDate(notification.created_at)
        }}</time>
        <span v-if="!notification.is_read" class="notification-card__pill">New</span>
      </div>

      <h3 class="notification-card__title">{{ notification.title }}</h3>

      <notification-message
        class="notification-card__message"
        :message="notification.message"
        :expandable="expandable"
      />

      <div class="notification-card__actions">
        <ui-button
          v-if="getNotificationRedirectUrl(notification)"
          size="sm"
          variant="secondary"
          type="button"
          @click.stop="emit('redirect', notification)"
        >
          <external-link-icon class="action-icon" />
          Open
        </ui-button>
        <ui-button
          size="sm"
          variant="ghost"
          type="button"
          @click.stop="emit('delete', notification.id)"
        >
          <trash-icon class="action-icon" />
          Delete
        </ui-button>
      </div>
    </div>
  </ui-card>

  <div
    v-else
    :class="['notification-item', { 'is-unread': !notification.is_read }]"
    @click="!notification.is_read && emit('mark-read', notification.id)"
  >
    <div class="notification-header">
      <div class="notification-title-group">
        <span v-if="!notification.is_read" class="unread-dot"></span>
        <ui-badge v-if="showEventBadge" variant="gray">{{
          formatNotificationEventType(notification.event_type)
        }}</ui-badge>
        <h4 class="notification-title">
          <ui-truncate :text="notification.title" />
        </h4>
      </div>
      <div class="notification-actions">
        <span class="notification-date">{{ formatNotificationDate(notification.created_at) }}</span>
        <button
          v-if="getNotificationRedirectUrl(notification)"
          class="icon-btn"
          type="button"
          title="Go to page"
          @click.stop="emit('redirect', notification)"
        >
          <external-link-icon class="icon" />
        </button>
        <button
          class="icon-btn danger"
          type="button"
          title="Delete notification"
          @click.stop="emit('delete', notification.id)"
        >
          <trash-icon class="icon" />
        </button>
      </div>
    </div>
    <div class="notification-body">
      <notification-message
        :message="notification.message"
        :expandable="expandable"
        clamp
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiTruncate from '@/components/ui/UiTruncate'
import ExternalLinkIcon from '@/icons/ExternalLinkIcon.vue'
import TrashIcon from '@/icons/TrashIcon.vue'
import NotificationMessage from './NotificationMessage.vue'
import {
  formatNotificationDate,
  formatNotificationEventType,
  getNotificationCategory,
  getNotificationRedirectUrl,
} from '../../composables/useNotifications'
import type { NotificationResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  notification: NotificationResponse
  showEventBadge?: boolean
  expandable?: boolean
  layout?: 'compact' | 'list'
}

const props = withDefaults(defineProps<Props>(), {
  showEventBadge: false,
  expandable: false,
  layout: 'compact',
})

const emit = defineEmits<{
  (e: 'mark-read', id: number): void
  (e: 'delete', id: number): void
  (e: 'redirect', notification: NotificationResponse): void
}>()

function onListCardClick(): void {
  if (props.layout !== 'list' || props.notification.is_read) return
  emit('mark-read', props.notification.id)
}
</script>

<style scoped>
.notification-card {
  padding: 0;
  overflow: hidden;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.notification-card :deep(.card-body) {
  gap: 0;
}

.notification-card:hover {
  border-color: color-mix(in srgb, var(--primary) 22%, var(--border));
  box-shadow: 0 8px 24px color-mix(in srgb, var(--foreground) 8%, transparent);
}

.notification-card--unread {
  border-color: color-mix(in srgb, var(--primary) 40%, var(--border));
  background: color-mix(in srgb, var(--primary) 5%, var(--card));
  cursor: pointer;
}

.notification-card__body {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  padding: 1rem 1.2rem 1.05rem;
}

.notification-card__meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem 0.45rem;
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  color: var(--muted-foreground);
}

.notification-card__category {
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.notification-card__meta-sep {
  opacity: 0.65;
}

.notification-card__date {
  font-weight: 500;
}

.notification-card__pill {
  margin-left: auto;
  padding: 0.12rem 0.45rem;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.notification-card__title {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-lg);
  line-height: var(--text-lg--line-height);
  font-weight: 800;
  overflow-wrap: anywhere;
}

.notification-card__message {
  font-size: var(--text-sm);
  line-height: 1.55;
  color: var(--muted-foreground);
}

.notification-card__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.45rem;
  margin-top: 0.35rem;
  padding-top: 0.65rem;
  border-top: 1px solid var(--border);
}

.action-icon {
  width: 14px;
  height: 14px;
}

.notification-item {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
}

.notification-item:last-child {
  border-bottom: 0;
}

.notification-item.is-unread {
  background: var(--primary-soft);
  cursor: pointer;
}

.notification-item.is-unread:hover {
  background: var(--hover);
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  gap: 0.75rem;
}

.notification-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  min-width: 0;
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--primary);
  flex-shrink: 0;
}

.notification-title {
  margin: 0;
  min-width: 0;
  flex: 1;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
  font-weight: 600;
  overflow-wrap: anywhere;
}

.notification-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.notification-date {
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  color: var(--muted-foreground);
  white-space: nowrap;
}

.icon-btn {
  background: none;
  border: none;
  color: var(--muted-foreground);
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  color: var(--primary);
  background: var(--primary-soft);
}

.icon-btn.danger:hover {
  color: var(--destructive);
  background: var(--destructive-soft);
}

.icon-btn .icon {
  width: 16px;
  height: 16px;
}

.notification-body {
  font-size: var(--text-sm);
  line-height: 1.4;
  color: var(--foreground);
  margin-left: 0.5rem;
}

@media (max-width: 760px) {
  .notification-card__pill {
    margin-left: 0;
  }

  .notification-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
