<template>
  <ui-card :id="`news-${item.id}`" class="news-item">
    <template #header>
      <div class="news-item-head">
        <div>
          <h3>{{ item.title }}</h3>
          <p class="meta">{{ item.created_by_name || 'Unknown author' }} · {{ formattedDate }}</p>
        </div>
        <div v-if="canModify" class="news-actions">
          <ui-button class="news-action-btn" variant="secondary" @click="$emit('edit', item)">
            Edit
          </ui-button>
          <ui-button class="news-action-btn" variant="danger" @click="$emit('delete', item)">
            Delete
          </ui-button>
        </div>
      </div>
    </template>

    <div
      class="news-content-wrap"
      :class="{ collapsible: isExpandable, expanded: isExpandable && isExpanded }"
    >
      <news-content-viewer :content="item.content" />
    </div>
    <ui-button v-if="isExpandable" size="sm" variant="secondary" @click="isExpanded = !isExpanded">
      {{ isExpanded ? 'Show less' : 'Show more' }}
    </ui-button>
  </ui-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import NewsContentViewer from '../components/NewsContentViewer.vue'
import type { NewsArticle } from '@/api/.ts.schemas'

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
  display: grid;
  gap: 0.8rem;
  padding: 0.95rem;
  background: var(--muted);
}
.news-item-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.8rem;
}

.news-item-head > div:first-child {
  min-width: 0;
}

.news-item-head h3 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
  word-break: break-word;
}

.news-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.45rem;
}

.news-action-btn {
  min-width: 76px;
  min-height: 40px;
}

.news-content-wrap {
  position: relative;
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
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0), var(--muted));
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
  word-break: break-word;
}

@media (max-width: 700px) {
  .news-item-head {
    flex-direction: column;
  }

  .news-actions {
    justify-content: flex-start;
  }
}
</style>
