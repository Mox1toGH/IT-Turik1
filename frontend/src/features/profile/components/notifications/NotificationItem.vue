<template>
  <div
    :class="['notification-item', { 'is-unread': !notification.is_read }]"
    @click="!notification.is_read && emit('mark-read', notification.id)"
  >
    <div class="notification-header">
      <div class="notification-title-group">
        <span v-if="!notification.is_read" class="unread-dot"></span>
        <ui-badge v-if="showEventBadge" variant="gray">{{ notification.event_type }}</ui-badge>
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
      <ui-expandable-text v-if="expandable" :lines="2">
        <p class="notification-message">
          <template v-for="(part, index) in parseNotificationMessage(notification.message)" :key="index">
            <a
              v-if="part.type === 'user'"
              :href="`/users/${part.id}`"
              class="user-link"
              @click.stop
            >
              {{ part.text }}
            </a>
            <router-link
              v-else-if="part.type === 'team'"
              :to="`/teams/${part.id}`"
              class="user-link"
              @click.stop
            >
              {{ part.text }}
            </router-link>
            <router-link
              v-else-if="part.type === 'news'"
              :to="`/news#news-${part.id}`"
              class="user-link"
              @click.stop
            >
              {{ part.text }}
            </router-link>
            <span v-else>{{ part.text }}</span>
          </template>
        </p>
      </ui-expandable-text>
      <p v-else class="notification-message notification-message--clamp">
        <template v-for="(part, index) in parseNotificationMessage(notification.message)" :key="index">
          <a
            v-if="part.type === 'user'"
            :href="`/users/${part.id}`"
            class="user-link"
            @click.stop
          >
            {{ part.text }}
          </a>
          <router-link
            v-else-if="part.type === 'team'"
            :to="`/teams/${part.id}`"
            class="user-link"
            @click.stop
          >
            {{ part.text }}
          </router-link>
          <router-link
            v-else-if="part.type === 'news'"
            :to="`/news#news-${part.id}`"
            class="user-link"
            @click.stop
          >
            {{ part.text }}
          </router-link>
          <span v-else>{{ part.text }}</span>
        </template>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiExpandableText from '@/components/ui/UiExpandableText'
import UiTruncate from '@/components/ui/UiTruncate'
import ExternalLinkIcon from '@/icons/ExternalLinkIcon.vue'
import TrashIcon from '@/icons/TrashIcon.vue'
import {
  formatNotificationDate,
  getNotificationRedirectUrl,
  parseNotificationMessage,
} from '../../composables/useNotifications'
import type { NotificationResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  notification: NotificationResponse
  showEventBadge?: boolean
  expandable?: boolean
}

withDefaults(defineProps<Props>(), {
  showEventBadge: false,
  expandable: false,
})

const emit = defineEmits<{
  (e: 'mark-read', id: number): void
  (e: 'delete', id: number): void
  (e: 'redirect', notification: NotificationResponse): void
}>()
</script>

<style scoped>
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

.notification-message {
  margin: 0;
  overflow-wrap: anywhere;
}

.notification-message--clamp {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.user-link {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
}

.user-link:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
}

@media (max-width: 760px) {
  .notification-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
