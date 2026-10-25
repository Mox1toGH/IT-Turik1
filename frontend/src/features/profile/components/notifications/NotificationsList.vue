<template>
  <ui-query-block :query="query" title="notifications">
    <ui-query-field>
      <template #skeleton>
        <div class="loading-state">
          <ui-skeleton variant="rect" height="132px" width="100%" />
          <ui-skeleton variant="rect" height="132px" width="100%" />
          <ui-skeleton variant="rect" height="132px" width="100%" />
        </div>
      </template>

      <template #default>
        <p v-if="isEmpty" class="state-text">You have no notifications.</p>
        <div v-else class="notifications-feed">
          <notification-item
            v-for="notification in items"
            :key="notification.id"
            :notification="notification"
            layout="list"
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
    </ui-query-field>
  </ui-query-block>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiButton from '@/components/ui/UiButton'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import NotificationItem from './NotificationItem.vue'
import type { QueryLike } from '@/composables/useQueryState'
import type { NotificationResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  query: QueryLike
  items: NotificationResponse[]
  page: number
  totalPages: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'mark-read', id: number): void
  (e: 'delete', id: number): void
  (e: 'redirect', notification: NotificationResponse): void
  (e: 'prev'): void
  (e: 'next'): void
}>()

const isEmpty = computed(() => props.items.length === 0)
</script>

<style scoped>
.loading-state {
  padding: 0.5rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.state-text {
  margin: 0;
  color: var(--muted-foreground);
  font-size: var(--text-base);
}

.notifications-feed {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.25rem;
}

.page-info {
  font-size: var(--text-sm);
  color: var(--muted-foreground);
  font-weight: 500;
}

@media (max-width: 760px) {
  .pagination-controls {
    flex-wrap: wrap;
  }
}
</style>
