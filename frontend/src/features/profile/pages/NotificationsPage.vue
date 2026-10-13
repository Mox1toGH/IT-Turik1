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

        <notifications-filters
          :has-unread="notifications.hasUnread.value"
          :has-notifications="notifications.hasNotifications.value"
          :is-marking-all="notifications.isMarkingAll.value"
          :is-deleting-all="notifications.isDeletingAll.value"
          @mark-all-read="notifications.handleMarkAllRead"
          @delete-all="notifications.requestDeleteAllConfirm"
          @open-settings="isSettingsModalOpen = true"
        />
      </header>

      <div class="notifications-rule" aria-hidden="true"></div>

      <ui-section aria-label="Notifications list">
        <notifications-list
          :items="notifications.notificationsData.value?.items ?? []"
          :is-loading="notifications.isLoading.value"
          :error="notifications.error.value"
          :page="page"
          :total-pages="notifications.totalPages.value"
          @mark-read="notifications.handleMarkRead"
          @delete="notifications.requestDeleteConfirm"
          @redirect="handleRedirect"
          @prev="prevPage"
          @next="nextPage"
        />
      </ui-section>
    </section>

    <notification-settings-modal v-model:is-open="isSettingsModalOpen" />

    <ui-modal
      v-model="notifications.isConfirmModalOpen.value"
      :title="notifications.confirmModalConfig.value.title"
      max-width="400px"
      @close="notifications.isConfirmModalOpen.value = false"
    >
      <p>{{ notifications.confirmModalConfig.value.message }}</p>
      <template #footer>
        <ui-button
          size="sm"
          variant="secondary"
          @click="notifications.isConfirmModalOpen.value = false"
          >Cancel</ui-button
        >
        <ui-button
          size="sm"
          :variant="notifications.confirmModalConfig.value.confirmVariant"
          :disabled="notifications.isDeletingAll.value"
          @click="notifications.confirmModalConfig.value.onConfirm"
        >
          {{ notifications.isDeletingAll.value ? 'Deleting...' : 'Confirm' }}
        </ui-button>
      </template>
    </ui-modal>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UiModal from '@/components/ui/UiModal'
import UiButton from '@/components/ui/UiButton'
import UiSection from '@/components/ui/UiSection'
import NotificationSettingsModal from '../components/notifications/NotificationSettingsModal.vue'
import NotificationsFilters from '../components/notifications/NotificationsFilters.vue'
import NotificationsList from '../components/notifications/NotificationsList.vue'
import { useNotifications } from '../composables/useNotifications'
import type { NotificationResponse } from '@/api/backendAPINinja.schemas'

const isSettingsModalOpen = ref(false)
const page = ref(1)

const notifications = useNotifications({ page })

const prevPage = (): void => {
  if (page.value > 1) page.value--
}

const nextPage = (): void => {
  if (page.value < notifications.totalPages.value) page.value++
}

const handleRedirect = (notification: NotificationResponse): void => {
  notifications.handleNotificationClick(notification)
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
  color: var(--muted-foreground);
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

.notifications-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--border);
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
}
</style>
