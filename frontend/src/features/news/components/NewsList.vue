<template>
  <ui-section title="Latest news" description="Fresh announcements from the platform team.">
    <ui-query-block :query="query" title="news">
      <ui-query-field>
        <template #skeleton>
          <div class="news-grid">
            <div class="news-item-skeleton" v-for="i in 2" :key="i">
              <ui-skeleton variant="rect" width="65%" />
              <ui-skeleton variant="rect" width="45%" />
              <ui-skeleton variant="rect" height="90px" width="100%" />
            </div>
          </div>
        </template>

        <template #default>
          <div v-if="isEmpty" class="news-empty">
            <p class="card-muted">No news yet</p>
            <p class="text-base">Announcements will appear here when they are published.</p>
          </div>
          <div v-else class="news-grid">
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
            <ui-pagination
              v-model="currentPageModel"
              :total-items="totalNews"
              :page-size="pageSize"
            />
          </div>
        </template>
      </ui-query-field>
    </ui-query-block>
  </ui-section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiPagination from '@/components/ui/UiPagination'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSection from '@/components/ui/UiSection'
import UiSkeleton from '@/components/ui/UiSkeleton'
import NewsItemCard from './NewsItemCard.vue'
import type { QueryLike } from '@/composables/useQueryState'
import type { NewsArticle } from '../types'

const props = defineProps<{
  query: QueryLike
  items: NewsArticle[]
  totalNews: number
  pageSize: number
  canModify: (item: NewsArticle) => boolean
}>()

defineEmits<{
  edit: [item: NewsArticle]
  delete: [item: NewsArticle]
}>()

const currentPageModel = defineModel<number>('currentPage', { required: true })

const isEmpty = computed(() => props.items.length === 0)
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
</style>
