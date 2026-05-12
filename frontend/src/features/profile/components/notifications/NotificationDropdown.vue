<template>
  <div class="notification-dropdown-container" ref="dropdownContainer">
    <button class="notification-bell" @click="toggleDropdown" :class="{ active: isOpen }">
      <bell-icon class="icon" />
      <span v-if="unreadCount?.unread_count" class="badge">
        {{ unreadCount.unread_count > 99 ? '99+' : unreadCount.unread_count }}
      </span>
    </button>

    <div v-if="isOpen" class="dropdown-menu">
      <div class="dropdown-header">
        <h4>Notifications</h4>
        <div class="header-actions">
          <button 
            v-if="hasUnread" 
            class="action-link" 
            @click="handleMarkAllRead"
            :disabled="isMarkingAll"
          >
            Mark read
          </button>
          <button 
            v-if="hasNotifications" 
            class="action-link danger" 
            @click="handleDeleteAll"
            :disabled="isDeletingAll"
          >
            Delete all
          </button>
        </div>
      </div>

      <div class="dropdown-body">
        <div v-if="isLoading" class="state-message">Loading...</div>
        <div v-else-if="error" class="state-message">Error loading</div>
        <div v-else-if="unreadNotifications.length === 0" class="state-message">
          There are currently no new notifications
        </div>
          <div v-else class="notifications-list">
            <div 
              v-for="notification in unreadNotifications" 
              :key="notification.id"
              class="notification-item is-unread"
              @click="markAsRead(notification.id)"
            >
              <div class="item-content">
                <div class="item-title-row">
                  <span v-if="!notification.is_read" class="unread-dot"></span>
                  <span class="item-title">{{ notification.title }}</span>
                  <button 
                    v-if="getRedirectUrl(notification)"
                    class="redirect-btn-mini" 
                    @click.stop="handleNotificationClick(notification, $event)"
                    title="Go to page"
                  >
                    <external-link-icon class="icon" />
                  </button>
                  <button 
                    class="delete-btn-mini" 
                    @click.stop="handleDelete(notification.id)"
                    title="Delete notification"
                  >
                    <trash-icon class="icon" />
                  </button>
                </div>
                <span class="item-message">
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
                </span>
                <span class="item-date">{{ formatDate(notification.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

      <div class="dropdown-footer">
        <ui-button size="sm" variant="secondary" style="width: 100%" @click="goToAllNotifications">
          View all notifications
        </ui-button>
      </div>
    </div>

    <ui-confirm-modal
      v-model="isConfirmModalOpen"
      :title="confirmModalConfig.title"
      :message="confirmModalConfig.message"
      :confirm-variant="confirmModalConfig.confirmVariant"
      :loading="isDeletingAll"
      @confirm="confirmModalConfig.onConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import BellIcon from '@/icons/BellIcon.vue'
import ExternalLinkIcon from '@/icons/ExternalLinkIcon.vue'

import TrashIcon from '@/icons/TrashIcon.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import { 
  useNotifications, 
  useUnreadCount, 
  useMarkAsRead, 
  useMarkAllAsRead,
  useDeleteNotification,
  useDeleteAllNotifications
} from '@/api/queries/notifications'
import type { Notification } from '@/api/services/notifications/types'

const isOpen = ref(false)
const dropdownContainer = ref<HTMLElement | null>(null)
const router = useRouter()

const { data: notifications, isLoading, error } = useNotifications(1, 100)
const { data: unreadCount } = useUnreadCount()
const { mutate: markAsRead } = useMarkAsRead()
const { mutate: markAllAsRead, isPending: isMarkingAll } = useMarkAllAsRead()
const { mutate: deleteNotification } = useDeleteNotification()
const { mutate: deleteAllNotifications, isPending: isDeletingAll } = useDeleteAllNotifications()

// Confirmation Modal State
const isConfirmModalOpen = ref(false)
const confirmModalConfig = ref({
  title: '',
  message: '',
  onConfirm: () => {},
  confirmVariant: 'danger' as const
})

const unreadNotifications = computed(() => {
  return notifications.value?.results?.filter((n) => !n.is_read) || []
})

const hasUnread = computed(() => unreadNotifications.value.length > 0)
const hasNotifications = computed(() => (notifications.value?.results?.length ?? 0) > 0)

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const closeDropdown = (e: MouseEvent) => {
  if (dropdownContainer.value && !dropdownContainer.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

const handleMarkAllRead = () => {
  markAllAsRead()
}

const handleDelete = (id: number) => {
  confirmModalConfig.value = {
    title: 'Delete Notification',
    message: 'Delete this notification?',
    confirmVariant: 'danger',
    onConfirm: () => {
      deleteNotification(id, {
        onSuccess: () => {
          isConfirmModalOpen.value = false
        },
        onError: (err) => {
          console.error('Failed to delete notification from dropdown:', err)
        },
      })
    }
  }
  isConfirmModalOpen.value = true
}

const handleDeleteAll = () => {
  confirmModalConfig.value = {
    title: 'Delete All Notifications',
    message: 'Delete ALL notifications? This cannot be undone.',
    confirmVariant: 'danger',
    onConfirm: () => {
      deleteAllNotifications(undefined, {
        onSuccess: () => {
          isConfirmModalOpen.value = false
        },
        onError: (err) => {
          console.error('Failed to delete all notifications from dropdown:', err)
        },
      })
    }
  }
  isConfirmModalOpen.value = true
}

const handleNotificationClick = (notification: any, event: Event) => {
  if (!notification.is_read) {
    markAsRead(notification.id)
  }

  const url = getRedirectUrl(notification)
  if (url) {
    isOpen.value = false
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


const goToAllNotifications = () => {
  isOpen.value = false
  router.push('/profile/notifications')
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

onMounted(() => {
  document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
})
</script>

<style scoped>
.notification-dropdown-container {
  position: relative;
}

.notification-bell {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  color: var(--foreground);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.notification-bell:hover,
.notification-bell.active {
  background-color: var(--secondary);
}

.notification-bell .icon {
  width: 20px;
  height: 20px;
}

.notification-bell .badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background-color: var(--destructive);
  color: white;
  font-size: 0.65rem;
  font-weight: bold;
  padding: 2px 5px;
  border-radius: 10px;
  line-height: 1;
  min-width: 16px;
  text-align: center;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: -10px;
  width: 320px;
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 100;
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border);
}

.dropdown-header h4 {
  margin: 0;
  font-size: 1rem;
}

.action-link {
  background: none;
  border: none;
  color: var(--brand-600);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.action-link:hover:not(:disabled) {
  text-decoration: underline;
  color: var(--brand-700);
}

.action-link.danger {
  color: var(--destructive);
}

.action-link.danger:hover:not(:disabled) {
  color: #c4000a;
}

.action-link:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.dropdown-body {
  max-height: 350px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.state-message {
  padding: 2rem;
  text-align: center;
  color: var(--muted-foreground);
  font-size: 0.9rem;
}

.notifications-list {
  display: flex;
  flex-direction: column;
}

.notification-item {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
  transition: background-color 0.2s ease;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item.is-unread {
  background: color-mix(in srgb, var(--brand-500) 5%, transparent);
  cursor: pointer;
}

.notification-item.is-unread:hover {
  background: color-mix(in srgb, var(--brand-500) 10%, transparent);
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.item-title-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.unread-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--brand-500);
  flex-shrink: 0;
}

.item-title {
  font-weight: 600;
  font-size: 0.85rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.redirect-btn-mini {
  background: none;
  border: none;
  color: var(--muted-foreground);
  padding: 2px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
  opacity: 0;
}

.notification-item:hover .redirect-btn-mini {
  opacity: 1;
}

.redirect-btn-mini:hover {
  color: var(--brand-600);
  background: color-mix(in srgb, var(--brand-500) 10%, transparent);
}

.redirect-btn-mini .icon {
  width: 12px;
  height: 12px;
}

.delete-btn-mini {
  background: none;
  border: none;
  color: var(--muted-foreground);
  padding: 2px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
  opacity: 0;
}

.notification-item:hover .delete-btn-mini {
  opacity: 1;
}

.delete-btn-mini:hover {
  color: #c4000a;
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
}

.delete-btn-mini .icon {
  width: 12px;
  height: 12px;
}

.item-message {
  font-size: 0.8rem;
  color: var(--foreground);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-date {
  font-size: 0.7rem;
  color: var(--muted-foreground);
}

.dropdown-footer {
  padding: 0.75rem;
  border-top: 1px solid var(--border);
  background: var(--muted);
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
