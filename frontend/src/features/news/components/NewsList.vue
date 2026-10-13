<template>
  <ui-section title="Latest news" description="Fresh announcements from the platform team.">
    <div v-if="status === 'loading'" class="news-grid">
      <div class="news-item-skeleton" v-for="i in 2" :key="i">
        <ui-skeleton variant="rect" width="65%" />
        <ui-skeleton variant="rect" width="45%" />
        <ui-skeleton variant="rect" height="90px" width="100%" />
      </div>
    </div>

    <div v-else-if="status === 'error'" class="news-state">
      <ui-card-error
        title="news"
        :error-code="errorCode"
        :is-fetching="isFetching"
        @retry="emit('retry')"
      />
    </div>

    <div v-else-if="status === 'empty'" class="news-state">
      <p class="card-muted">No news yet</p>
      <p class="text-base">Announcements will appear here when they are published.</p>
    </div>

    <div v-else class="news-body">
      <div v-if="isStale" class="stale-banner" role="status">
        <span>Update failed</span>
        <button type="button" :disabled="isFetching" @click="emit('retry')">
          {{ isFetching ? 'Retrying…' : 'Retry' }}
        </button>
      </div>

      <div :class="{ dimmed: isFetching }" :aria-busy="isFetching || undefined">
        <div class="news-grid">
          <news-item-card
            v-for="item in items"
            :key="item.id"
            :item="item"
            :can-modify="canModify(item)"
            @edit="$emit('edit', $event)"
            @delete="$emit('delete', $event)"
          />
        </div>

        <div v-if="totalNews > pageSize" class="pagination-row">
          <ui-pagination v-model="currentPageModel" :total-items="totalNews" :page-size="pageSize" />
        </div>
      </div>
    </div>
  </ui-section>
</template>

<script setup lang="ts">
import UiCardError from '@/components/ui/UiCardError'
import UiSection from '@/components/ui/UiSection'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiPagination from '@/components/ui/UiPagination'
import NewsItemCard from './NewsItemCard.vue'
import type { CardErrorCode, CardStatus } from '@/composables/useCardState'
import type { NewsArticleResponse } from '@/api/backendAPINinja.schemas.ts'

defineProps<{
  status: CardStatus
  errorCode: CardErrorCode
  isFetching: boolean
  isStale: boolean
  items: NewsArticleResponse[]
  totalNews: number
  totalPages: number
  pageSize: number
  canModify: (item: NewsArticleResponse) => boolean
}>()

const emit = defineEmits<{
  edit: [item: NewsArticleResponse]
  delete: [item: NewsArticleResponse]
  retry: []
}>()

const currentPageModel = defineModel<number>('currentPage', { required: true })
</script>

<style scoped>
.news-grid {
  display: grid;
  gap: 0.9rem;
  grid-template-columns: 1fr;
}

.news-item-skeleton {
  display: grid;
  gap: 0.65rem;
  padding: 1.2rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

.news-body {
  display: grid;
  gap: 1rem;
}

.news-state {
  display: grid;
  gap: 0.5rem;
  justify-items: center;
  text-align: center;
  padding: 2rem 0;
}

.card-muted {
  margin: 0;
  font-size: 0.9rem;
  color: var(--muted-foreground);
}

.pagination-row {
  display: flex;
  justify-content: center;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border);
}

.dimmed > * {
  opacity: 0.6;
}

.stale-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.35rem 0.6rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--subtle);
  color: var(--muted-foreground);
  font-size: 0.8rem;
}

.stale-banner button {
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  font-weight: 600;
  text-decoration: underline;
  cursor: pointer;
}

.stale-banner button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.stale-banner button:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}

.empty-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-height: 96px;
  padding: 1.35rem;
  border: 1px dashed var(--border);
  border-radius: 16px;
  background: var(--background);
}

.empty-icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--primary-soft);
  color: var(--primary);
  font-size: var(--text-2xl);
  font-weight: 800;
}

.empty-copy {
  min-width: 0;
}

.empty-copy h3,
.empty-copy p {
  margin: 0;
}

.empty-copy h3 {
  color: var(--foreground);
  font-weight: 800;
}

.empty-copy p {
  margin-top: 0.25rem;
  color: var(--muted-foreground);
}

.error-box {
  display: flex;
  height: 140px;
  justify-content: center;
  align-items: center;
}

@media (max-width: 700px) {
  .empty-row {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
