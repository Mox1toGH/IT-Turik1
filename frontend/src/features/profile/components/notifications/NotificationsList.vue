<template>
  <div v-if="isLoading" class="loading-state">
    <p class="text-muted">Loading notifications...</p>
  </div>
  <div v-else-if="error" class="error-state">
    <p>Error loading notifications.</p>
  </div>
  <div v-else-if="items.length === 0" class="empty-state">
    <p class="text-muted">You have no notifications.</p>
  </div>
  <div v-else class="notifications-list">
    <notification-item
      v-for="notification in items"
      :key="notification.id"
      :notification="notification"
      show-event-badge
      expandable
      @mark-read="emit('mark-read', $event)"
      @delete="emit('delete', $event)"
      @redirect="emit('redirect', $event)"
    />
  </div>

  <div v-if="totalPages > 1" class="pagination-controls">
    <ui-button size="sm" variant="secondary" :disabled="page === 1" @click="emit('prev')">
      Previous
    </ui-button>
    <span class="page-info">Page {{ page }} of {{ totalPages }}</span>
    <ui-button
      size="sm"
      variant="secondary"
      :disabled="page === totalPages"
      @click="emit('next')"
    >
      Next
    </ui-button>
  </div>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import NotificationItem from './NotificationItem.vue'
import type { NotificationResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  items: NotificationResponse[]
  isLoading: boolean
  error: unknown
  page: number
  totalPages: number
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'mark-read', id: number): void
  (e: 'delete', id: number): void
  (e: 'redirect', notification: NotificationResponse): void
  (e: 'prev'): void
  (e: 'next'): void
}>()
</script>

<style scoped>
.loading-state,
.error-state,
.empty-state {
  padding: 4rem 1rem;
  text-align: center;
  color: var(--muted-foreground);
}

.notifications-list {
  display: flex;
  flex-direction: column;
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
</style>
