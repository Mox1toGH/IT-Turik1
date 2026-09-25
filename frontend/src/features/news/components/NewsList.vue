<template>
  <ui-card v-if="isLoading" variant="panel">
    <template #header>
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Updates</p>
          <h2 class="text-3xl">Latest news</h2>
          <p class="section-subtitle text-base">Fresh announcements from the platform team.</p>
        </div>

        <div class="section-meta">
          <ui-skeleton variant="rect" width="98px" height="38px" />
        </div>
      </div>
    </template>
    <ui-skeleton-loader :loading="isLoading">
      <template #skeleton>
        <div class="news-grid">
          <ui-card class="news-item" v-for="i in 2" :key="i">
            <template #header>
              <ui-skeleton variant="rect" width="65%" />
              <ui-skeleton variant="rect" width="45%" />
            </template>
            <ui-skeleton variant="rect" height="90px" width="100%" />
          </ui-card>
        </div>
      </template>
    </ui-skeleton-loader>
  </ui-card>

  <ui-card v-else-if="isError" variant="panel" :isError="true">
    <template #error>
      <div class="error-box">
        <p>Failed to fetch news (code: {{ errorCode }})</p>
      </div>
    </template>
  </ui-card>

  <ui-card v-else-if="!items.length" variant="panel">
    <template #header>
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Updates</p>
          <h2 class="text-3xl">Latest news</h2>
          <p class="section-subtitle text-base">Fresh announcements from the platform team.</p>
        </div>

        <div class="section-meta">
          <span class="count-pill text-base">0 published</span>
        </div>
      </div>
    </template>

    <div class="empty-row">
      <div class="empty-icon" aria-hidden="true">+</div>
      <div class="empty-copy">
        <h3 class="text-lg">No news yet</h3>
        <p class="text-base">Announcements will appear here when they are published.</p>
      </div>
    </div>
  </ui-card>

  <ui-card v-else variant="panel">
    <template #header>
      <div class="section-head">
        <div>
          <div class="section-meta">
            <h2 class="text-3xl">Latest news</h2>
            <span class="count-pill text-base">{{ totalNews }} published</span>
          </div>
          <p class="section-subtitle text-base">Fresh announcements from the platform team.</p>
        </div>
      </div>
    </template>

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

    <ui-pagination
      v-if="totalNews > pageSize"
      v-model="currentPageModel"
      :total-items="totalNews"
      :page-size="pageSize"
    />
  </ui-card>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiPagination from '@/components/ui/UiPagination.vue'
import NewsItemCard from './NewsItemCard.vue'
import type { NewsArticleResponse } from '@/api/backendAPINinja.schemas.ts'

defineProps<{
  isLoading: boolean
  isError: boolean
  errorCode?: number | string
  items: NewsArticleResponse[]
  totalNews: number
  totalPages: number
  pageSize: number
  canModify: (item: NewsArticleResponse) => boolean
}>()

defineEmits<{
  edit: [item: NewsArticleResponse]
  delete: [item: NewsArticleResponse]
}>()

const currentPageModel = defineModel<number>('currentPage', { required: true })
</script>

<style scoped>
.section-head {
  justify-content: space-between;
  gap: 1rem;
}

.section-head h2 {
  margin: 1rem 0 0.45rem;
  font-family: var(--font-display);
  font-weight: 800;
}

.section-head .section-subtitle {
  margin: 0;
}

.section-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.count-pill {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--line-soft);
  border-radius: 999px;
  color: var(--muted-foreground);
  white-space: nowrap;
}

.news-grid {
  display: grid;
  gap: 0.9rem;
  grid-template-columns: 1fr;
}

.empty-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-height: 96px;
  padding: 1.35rem;
  border: 1px dashed var(--line-soft);
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
  background: color-mix(in srgb, var(--primary) 22%, transparent);
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
  .section-head,
  .empty-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .section-meta {
    min-height: 0;
    align-items: flex-start;
  }
}
</style>
