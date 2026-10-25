<template>
  <ui-card :id="`news-${item.id}`" class="news-item">
    <div class="news-body">
      <div class="news-item-head">
        <div class="news-head-copy">
          <ui-truncate :text="item.title" class="news-title" />
          <p class="meta">{{ item.created_by_name || 'Unknown author' }} · {{ formattedDate }}</p>
        </div>
        <ui-popover v-if="canModify" min-width="160px" header="News actions">
          <template #trigger>
            <ui-button
              class="news-action-trigger"
              variant="secondary"
              size="sm"
              aria-label="News actions"
            >
              <MoreHorizontal :size="18" />
            </ui-button>
          </template>
          <template #default="{ close }">
            <div class="news-actions">
              <ui-button
                class="news-action-btn"
                variant="secondary"
                @click="
                  close();
                  $emit('edit', item)
                "
              >
                Edit
              </ui-button>
              <ui-button
                class="news-action-btn"
                variant="danger"
                @click="
                  close();
                  $emit('delete', item)
                "
              >
                Delete
              </ui-button>
            </div>
          </template>
        </ui-popover>
      </div>

      <div
        :id="`news-content-${item.id}`"
        class="news-content-wrap"
        :class="{ collapsible: isExpandable, expanded: isExpandable && isExpanded }"
      >
        <news-content-viewer :content="item.content" />
      </div>
      <ui-button
        v-if="isExpandable"
        size="sm"
        variant="secondary"
        :aria-expanded="isExpanded"
        :aria-controls="`news-content-${item.id}`"
        @click="isExpanded = !isExpanded"
      >
        {{ isExpanded ? 'Show less' : 'Show more' }}
      </ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiCard from '@/components/ui/UiCard'
import UiButton from '@/components/ui/UiButton'
import UiTruncate from '@/components/ui/UiTruncate'
import UiPopover from '@/components/ui/UiPopover'
import { MoreHorizontal } from 'lucide-vue-next'
import NewsContentViewer from '../components/NewsContentViewer.vue'
import type { NewsArticle } from '../types'

const COLLAPSE_TEXT_LIMIT = 280

const props = defineProps<{
  item: NewsArticle
  canModify: boolean
}>()

defineEmits<{
  edit: [item: NewsArticle]
  delete: [item: NewsArticle]
}>()

function extractPlainText(value: unknown): string {
  if (!value || typeof value !== 'object') return ''
  const node = value as { text?: string; content?: unknown[] }
  const ownText = typeof node.text === 'string' ? node.text : ''
  const childText = Array.isArray(node.content)
    ? node.content.map((child) => extractPlainText(child)).join(' ')
    : ''
  return `${ownText} ${childText}`.trim()
}

const isExpanded = ref(false)
const isExpandable = computed(
  () => extractPlainText(props.item.content).length > COLLAPSE_TEXT_LIMIT,
)

const formattedDate = computed(() => {
  const value = props.item.created_at
  const date = typeof value === 'string' ? new Date(value) : value
  return date.toLocaleString()
})
</script>

<style scoped>
.news-item {
  height: 100%;
  min-width: 0;
  padding: 0;
  overflow: hidden;
}

.news-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
  padding: 1rem 1.25rem;
}

.news-item-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.8rem;
  min-width: 0;
}

.news-head-copy {
  min-width: 0;
  flex: 1 1 auto;
}

.news-title {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.1rem;
}

.news-actions {
  display: grid;
  gap: 0.35rem;
}

.news-action-btn { justify-content: flex-start; width: 100%; }
.news-action-trigger { flex: 0 0 auto; }

.news-content-wrap {
  position: relative;
  min-width: 0;
}
.news-content-wrap.collapsible {
  max-height: 180px;
  overflow: hidden;
  opacity: 0.96;
  transition:
    max-height 0.32s ease,
    opacity 0.24s ease;
  will-change: max-height, opacity;
}
.news-content-wrap.collapsible:not(.expanded)::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 48px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0), var(--card));
  pointer-events: none;
}
.news-content-wrap.collapsible.expanded {
  max-height: 2200px;
  opacity: 1;
}
.meta {
  margin: 0.35rem 0 0;
  color: var(--muted-foreground);
  font-size: 0.92rem;
  overflow-wrap: anywhere;
}

@media (max-width: 700px) {
  .news-item-head {
    flex-direction: column;
  }

}
</style>
