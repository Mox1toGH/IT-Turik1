<template>
  <div class="notification-dropdown-container" ref="dropdownContainer">
    <button class="notification-bell" @click="toggleDropdown" :class="{ active: isOpen }">
      <bell-icon class="icon" />
      <span v-if="notifications.unreadCount.value?.unread_count" class="badge">
        {{
          (notifications.unreadCount.value?.unread_count ?? 0) > 99
            ? '99+'
            : notifications.unreadCount.value?.unread_count
        }}
      </span>
    </button>

    <div v-if="isOpen" class="dropdown-menu">
      <div class="dropdown-header">
        <h4>Notifications</h4>
        <div class="header-actions">
          <button
            v-if="notifications.hasUnread.value"
            class="action-link"
            @click="notifications.handleMarkAllRead"
            :disabled="notifications.isMarkingAll.value"
          >
            Mark read
          </button>
          <button
            v-if="notifications.hasNotifications.value"
            class="action-link danger"
            @click="notifications.requestDeleteAllConfirm"
            :disabled="notifications.isDeletingAll.value"
          >
            Delete all
          </button>
        </div>
      </div>

      <div class="dropdown-body">
        <div v-if="notifications.isLoading.value" class="state-message">Loading...</div>
        <div v-else-if="notifications.error.value" class="state-message">Error loading</div>
        <div v-else-if="notifications.unreadNotifications.value.length === 0" class="state-message">
          There are currently no new notifications
        </div>
        <div v-else class="notifications-list">
          <notification-item
            v-for="notification in notifications.unreadNotifications.value"
            :key="notification.id"
            :notification="notification"
            @mark-read="notifications.handleMarkRead"
            @delete="notifications.requestDeleteConfirm"
            @redirect="handleRedirect"
          />
        </div>
      </div>

      <div class="dropdown-footer">
        <ui-button size="sm" variant="secondary" style="width: 100%" @click="goToAllNotifications">
          View all notifications
        </ui-button>
      </div>
    </div>
  </div>

  <ui-confirm-modal
    v-model="notifications.isConfirmModalOpen.value"
    :title="notifications.confirmModalConfig.value.title"
    :message="notifications.confirmModalConfig.value.message"
    :confirm-variant="notifications.confirmModalConfig.value.confirmVariant"
    :loading="notifications.isDeletingAll.value"
    @confirm="notifications.confirmModalConfig.value.onConfirm"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import BellIcon from '@/icons/BellIcon.vue'
import UiButton from '@/components/ui/UiButton'
import UiConfirmModal from '@/components/ui/UiConfirmModal'
import NotificationItem from './NotificationItem.vue'
import { useNotifications } from '../../composables/useNotifications'
import type { NotificationResponse } from '@/api/backendAPINinja.schemas'

const isOpen = ref(false)
const dropdownContainer = ref<HTMLElement | null>(null)
const router = useRouter()

const notifications = useNotifications()

const toggleDropdown = (): void => {
  isOpen.value = !isOpen.value
}

const closeDropdown = (e: MouseEvent): void => {
  if (dropdownContainer.value && !dropdownContainer.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

const handleRedirect = (notification: NotificationResponse): void => {
  isOpen.value = false
  notifications.handleNotificationClick(notification)
}

const goToAllNotifications = (): void => {
  isOpen.value = false
  router.push('/profile/notifications')
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
}

.notification-bell:hover,
.notification-bell.active {
  background-color: var(--subtle);
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
  color: var(--primary-foreground);
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
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-overlay);
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
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.action-link:hover:not(:disabled) {
  text-decoration: underline;
  text-underline-offset: 2px;
}

.action-link.danger {
  color: var(--destructive);
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

.dropdown-footer {
  padding: 0.75rem;
  border-top: 1px solid var(--border);
  background: var(--subtle);
}
</style>
