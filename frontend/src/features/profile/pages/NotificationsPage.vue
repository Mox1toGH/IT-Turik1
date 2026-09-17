<template>
  <section class="page-shell">
    <section class="notifications-section">
      <header class="notifications-hero">
        <div class="notifications-hero-copy">
          <div class="breadcrumb-label">
            <span>User Center</span>
            <span aria-hidden="true">/</span>
            <span>Notifications</span>
          </div>

          <h1 class="text-6xl">Notifications</h1>
          <p class="section-subtitle text-xl">
            Notifications older than 30 days are automatically deleted.
          </p>
        </div>

        <div class="hero-actions">
          <ui-card variant="stat" class="notifications-stat-card">
            <span class="text-sm">Unread:</span>
            <strong class="text-3xl">{{ unreadCount }}</strong>
          </ui-card>

          <ui-button
            variant="secondary"
            size="lg"
            :disabled="!hasUnread || isMarkingAll"
            @click="handleMarkAllRead"
          >
            Mark all read
          </ui-button>
          <ui-button
            variant="danger"
            size="lg"
            :disabled="!hasNotifications || isDeletingAll"
            @click="handleDeleteAll"
          >
            Delete all
          </ui-button>
          <ui-button size="lg" @click="isSettingsModalOpen = true">Settings</ui-button>
        </div>
      </header>

      <div class="notifications-rule" aria-hidden="true"></div>

      <ui-card variant="form" class="form-panel notifications-panel">
        <div v-if="isLoading" class="loading-state">
          <p class="text-muted">Loading notifications...</p>
        </div>
        <div v-else-if="error" class="error-state">
          <p>Error loading notifications.</p>
        </div>
        <div v-else-if="notificationsData?.results?.length === 0" class="empty-state">
          <p class="text-muted">You have no notifications.</p>
        </div>
        <div v-else class="notifications-list">
          <div
            v-for="notification in notificationsData?.results"
            :key="notification.id"
            :class="['notification-item', { 'is-unread': !notification.is_read }]"
            @click="!notification.is_read && handleMarkRead(notification.id)"
          >
            <div class="notification-header">
              <div class="notification-title-group">
                <span v-if="!notification.is_read" class="unread-dot"></span>
                <ui-badge variant="gray">{{ notification.event_type }}</ui-badge>
                <h4 class="notification-title">{{ notification.title }}</h4>
              </div>
              <div class="notification-actions">
                <span class="notification-date">{{ formatDate(notification.created_at) }}</span>
                <button
                  v-if="getRedirectUrl(notification)"
                  class="icon-btn"
                  @click.stop="handleNotificationClick(notification)"
                  title="Go to page"
                >
                  <external-link-icon class="icon" />
                </button>
                <button
                  class="icon-btn danger"
                  @click.stop="handleDelete(notification.id)"
                  title="Delete notification"
                >
                  <trash-icon class="icon" />
                </button>
              </div>
            </div>
            <div class="notification-body">
              <p class="notification-message">
                <template v-for="(part, index) in parseMessage(notification.message)" :key="index">
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
        </div>

        <div v-if="totalPages > 1" class="pagination-controls">
          <ui-button size="sm" variant="secondary" :disabled="page === 1" @click="prevPage">
            Previous
          </ui-button>
          <span class="page-info">Page {{ page }} of {{ totalPages }}</span>
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="page === totalPages"
            @click="nextPage"
          >
            Next
          </ui-button>
        </div>
      </ui-card>
    </section>

    <notification-settings-modal v-model:is-open="isSettingsModalOpen" />

    <ui-confirm-modal
      v-model="isConfirmModalOpen"
      :title="confirmModalConfig.title"
      :message="confirmModalConfig.message"
      :confirm-variant="confirmModalConfig.confirmVariant"
      :loading="isDeletingAll"
      @confirm="confirmModalConfig.onConfirm"
    />
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import ExternalLinkIcon from '@/icons/ExternalLinkIcon.vue'
import TrashIcon from '@/icons/TrashIcon.vue'
import NotificationSettingsModal from '../components/notifications/NotificationSettingsModal.vue'
import { useNotification } from '@/composables/useNotification'
import {
  useDeleteAllNotifications,
  useDeleteNotification,
  useListNotifications,
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
} from '@/api/notifications/notifications'
import type { Notification } from '@/api/.ts.schemas'

const isSettingsModalOpen = ref(false)
const page = ref(1)
const router = useRouter()

const {
  data: notificationsData,
  isLoading,
  error,
} = useListNotifications(computed(() => ({ page: page.value })))
const { mutate: markAsRead } = useMarkNotificationRead()
const { mutate: markAllAsRead, isPending: isMarkingAll } = useMarkAllNotificationsRead()
const { mutate: deleteNotification } = useDeleteNotification()
const { mutate: deleteAllNotifications, isPending: isDeletingAll } = useDeleteAllNotifications()
const { showNotification } = useNotification()

// Confirmation Modal State
const isConfirmModalOpen = ref(false)
const confirmModalConfig = ref({
  title: '',
  message: '',
  onConfirm: () => {},
  confirmVariant: 'danger' as const,
})

const unreadCount = computed(() => {
  return notificationsData.value?.results?.filter((n) => !n.is_read).length ?? 0
})

const hasUnread = computed(() => unreadCount.value > 0)

const hasNotifications = computed(() => {
  return (notificationsData.value?.results?.length ?? 0) > 0
})

const totalPages = computed(() => {
  if (!notificationsData.value?.count) return 1
  return Math.ceil(notificationsData.value.count / 10)
})

const prevPage = () => {
  if (page.value > 1) page.value--
}

const nextPage = () => {
  if (page.value < totalPages.value) page.value++
}

const handleMarkRead = (id: number) => {
  markAsRead({ id })
}

const handleMarkAllRead = () => {
  markAllAsRead(void 0, {
    onSuccess: () => showNotification('All notifications marked as read', 'success'),
    onError: (error) => showNotification(error.message, 'error'),
  })
}

const handleDelete = (id: number) => {
  confirmModalConfig.value = {
    title: 'Delete Notification',
    message: 'Are you sure you want to delete this notification?',
    confirmVariant: 'danger',
    onConfirm: () => {
      deleteNotification(
        { id },
        {
          onSuccess: () => {
            showNotification('Notification deleted', 'success')
            isConfirmModalOpen.value = false
          },
        },
      )
    },
  }
  isConfirmModalOpen.value = true
}

const handleDeleteAll = () => {
  confirmModalConfig.value = {
    title: 'Delete All Notifications',
    message: 'Are you sure you want to delete ALL notifications? This cannot be undone.',
    confirmVariant: 'danger',
    onConfirm: () => {
      deleteAllNotifications(undefined, {
        onSuccess: () => {
          showNotification('All notifications deleted', 'success')
          isConfirmModalOpen.value = false
        },
        onError: (error) => {
          showNotification(error.message, 'error')
        },
      })
    },
  }
  isConfirmModalOpen.value = true
}

const handleNotificationClick = (notification: Notification) => {
  if (!notification.is_read) {
    handleMarkRead(notification.id)
  }

  const url = getRedirectUrl(notification)
  if (url) {
    router.push(url)
  }
}

const getRedirectUrl = (notification: Notification) => {
  const type = notification.event_type

  // Only invitations go to /teams — recipient hasn't joined yet
  if (type === 'team_invitation_received') {
    return '/teams'
  }

  if (type.startsWith('team_')) {
    // Other team events can still link directly if possible
    const match = notification.message.match(/\[team:(\d+):.+?\]/)
    if (match) {
      return `/teams/${match[1]}`
    }
    return '/teams'
  }
  if (type === 'news_published') {
    const match = notification.message.match(/\[news:(\d+):.+?\]/)
    if (match) {
      return `/news#news-${match[1]}`
    }
    return '/news'
  }
  if (type.startsWith('tournament_')) {
    return '/tournaments'
  }
  if (type === 'jury_assignment_received') {
    return '/evaluation'
  }
  if (type === 'shop_order_status_changed') {
    return '/shop/orders'
  }
  if (type === 'points_balance_changed') {
    return '/profile/transaction-history'
  }
  return null
}

const parseMessage = (message: string) => {
  const parts = []
  // Matches [user:id:name], [team:id:name], or [news:id:title]
  const regex = /\[(user|team|news):(\d+):(.+?)\]/g
  let lastIndex = 0
  let match

  while ((match = regex.exec(message)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', text: message.substring(lastIndex, match.index) })
    }
    parts.push({
      type: match[1], // 'user' or 'team'
      id: match[2],
      text: match[3],
    })
    lastIndex = regex.lastIndex
  }

  if (lastIndex < message.length) {
    parts.push({ type: 'text', text: message.substring(lastIndex) })
  }

  return parts.length > 0 ? parts : [{ type: 'text', text: message }]
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}
</script>

<style scoped>
.notifications-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.notifications-hero-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.notifications-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.notifications-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.hero-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

.notifications-stat-card strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.notifications-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.notifications-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.form-panel.card {
  display: grid;
  gap: 0;
}

.loading-state,
.error-state,
.empty-state {
  padding: 4rem;
  text-align: center;
  color: var(--muted-foreground);
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.notification-item {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  background: var(--background);
  transition: background-color 0.2s ease;
}

.notification-item.is-unread {
  background: color-mix(in srgb, var(--brand-500) 5%, transparent);
  border-color: color-mix(in srgb, var(--brand-500) 20%, transparent);
  cursor: pointer;
}

.notification-item.is-unread:hover {
  background: color-mix(in srgb, var(--brand-500) 10%, transparent);
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  gap: 0.75rem;
}

.notification-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
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
  transition: all 0.2s;
}

.icon-btn:hover {
  color: var(--brand-600);
  background: color-mix(in srgb, var(--brand-500) 10%, transparent);
}

.icon-btn.danger:hover {
  color: var(--destructive);
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
}

.icon-btn .icon {
  width: 16px;
  height: 16px;
}

.notification-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--brand-500);
  flex-shrink: 0;
}

.notification-title {
  margin: 0;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
  font-weight: 600;
  overflow-wrap: anywhere;
}

.notification-date {
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  color: var(--muted-foreground);
  white-space: nowrap;
}

.notification-body {
  font-size: var(--text-sm);
  line-height: 1.4;
  color: var(--foreground);
  margin-left: 0.5rem;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

.page-info {
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  color: var(--muted-foreground);
  font-weight: 500;
}

.user-link {
  color: var(--brand-600);
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.user-link:hover {
  color: var(--brand-700);
  text-decoration: underline;
}

@media (max-width: 760px) {
  .notifications-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .notifications-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .notifications-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }

  .notification-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
