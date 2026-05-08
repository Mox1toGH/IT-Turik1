<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">User Center</p>
            <h1 class="section-title profile-title">Notifications</h1>
            <p class="meta">Notifications older than 30 days are automatically deleted.</p>
          </div>
          <div class="header-actions">
            <ui-button
              variant="secondary"
              size="sm"
              @click="handleMarkAllRead"
              :disabled="!hasUnread || isMarkingAll"
            >
              Mark all read
            </ui-button>
            <ui-button 
              variant="danger" 
              size="sm" 
              @click="handleDeleteAll" 
              :disabled="!hasNotifications || isDeletingAll"
            >
              Delete all
            </ui-button>
            <ui-button size="sm" @click="isSettingsModalOpen = true"> Settings </ui-button>
          </div>
        </div>
      </template>

      <div v-if="isLoading" class="loading-state">
        <p>Loading notifications...</p>
      </div>
      <div v-else-if="error" class="error-state">
        <p>Error loading notifications.</p>
      </div>
      <div v-else-if="notificationsData?.results?.length === 0" class="empty-state">
        <p>You have no notifications.</p>
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
                class="redirect-btn"
                @click.stop="handleNotificationClick(notification, $event)"
                title="Go to page"
              >
                <external-link-icon class="icon" />
              </button>
              <button 
                class="delete-btn" 
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
                <span v-else>{{ part.text }}</span>
              </template>
            </p>
          </div>
        </div>
      </div>

      <div v-if="totalPages > 1" class="pagination-controls">
        <ui-button size="sm" variant="secondary" :disabled="page === 1" @click="prevPage"
          >Previous</ui-button
        >
        <span class="page-info">Page {{ page }} of {{ totalPages }}</span>
        <ui-button size="sm" variant="secondary" :disabled="page === totalPages" @click="nextPage"
          >Next</ui-button
        >
      </div>
    </ui-card>

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
import { 
  useNotifications, 
  useMarkAsRead, 
  useMarkAllAsRead,
  useDeleteNotification,
  useDeleteAllNotifications
} from '@/api/queries/notifications'
import { useNotification } from '@/composables/useNotification'

const isSettingsModalOpen = ref(false)
const page = ref(1)
const router = useRouter()

const { data: notificationsData, isLoading, error } = useNotifications(page)
const { mutate: markAsRead } = useMarkAsRead()
const { mutate: markAllAsRead, isPending: isMarkingAll } = useMarkAllAsRead()
const { mutate: deleteNotification } = useDeleteNotification()
const { mutate: deleteAllNotifications, isPending: isDeletingAll } = useDeleteAllNotifications()
const { showNotification } = useNotification()

// Confirmation Modal State
const isConfirmModalOpen = ref(false)
const confirmModalConfig = ref({
  title: '',
  message: '',
  onConfirm: () => {},
  confirmVariant: 'danger' as const
})

const hasUnread = computed(() => {
  return notificationsData.value?.results?.some((n) => !n.is_read) ?? false
})

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
  markAsRead(id)
}

const handleMarkAllRead = () => {
  markAllAsRead(undefined, {
    onSuccess: () => showNotification('All notifications marked as read', 'success'),
    onError: () => showNotification('Failed to mark notifications as read', 'error'),
  })
}

const handleDelete = (id: number) => {
  confirmModalConfig.value = {
    title: 'Delete Notification',
    message: 'Are you sure you want to delete this notification?',
    confirmVariant: 'danger',
    onConfirm: () => {
      deleteNotification(id, {
        onSuccess: () => {
          showNotification('Notification deleted', 'success')
          isConfirmModalOpen.value = false
        },
        onError: (err) => {
          console.error('Failed to delete notification:', err)
          showNotification('Failed to delete notification', 'error')
        }
      })
    }
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
        onError: (err) => {
          console.error('Failed to delete all notifications:', err)
          showNotification('Failed to delete notifications', 'error')
        }
      })
    }
  }
  isConfirmModalOpen.value = true
}

const handleNotificationClick = (notification: any, event: Event) => {
  if (!notification.is_read) {
    handleMarkRead(notification.id)
  }

  const url = getRedirectUrl(notification)
  if (url) {
    router.push(url)
  }
}

const getRedirectUrl = (notification: any) => {
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
  return null
}

const parseMessage = (message: string) => {
  const parts = []
  // Matches [user:id:name] or [team:id:name]
  const regex = /\[(user|team):(\d+):(.+?)\]/g
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
.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.profile-title {
  margin-top: 0.2rem;
}

.meta {
  margin: 0;
  font-size: 0.86rem;
  color: var(--muted-foreground);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
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
  margin-top: 1rem;
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
}

.notification-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.redirect-btn {
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

.redirect-btn:hover {
  color: var(--brand-600);
  background: color-mix(in srgb, var(--brand-500) 10%, transparent);
}

.redirect-btn .icon {
  width: 16px;
  height: 16px;
}

.delete-btn {
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

.delete-btn:hover {
  color: #c4000a;
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
}

.delete-btn .icon {
  width: 16px;
  height: 16px;
}

.notification-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--brand-500);
}

.notification-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.notification-date {
  font-size: 0.8rem;
  color: var(--muted-foreground);
}

.notification-body {
  font-size: 0.9rem;
  color: var(--foreground);
  line-height: 1.4;
  margin-left: 0.5rem;
}

@media (max-width: 760px) {
  .head {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
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
  font-size: 0.9rem;
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
</style>
