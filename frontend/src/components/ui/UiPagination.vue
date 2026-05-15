<template>
  <nav class="pagination" aria-label="Pagination">
    <div v-if="showSummary" class="summary">
      Showing {{ fromItem }}-{{ toItem }} of {{ totalItems }}
    </div>

    <div class="controls">
      <ui-button
        size="sm"
        variant="secondary"
        :disabled="currentPage <= 1"
        @click="emit('update:modelValue', currentPage - 1)"
      >
        Prev
      </ui-button>

      <button
        v-for="item in pageItems"
        :key="`page-${item}`"
        type="button"
        class="page-pill"
        :class="{ active: item === currentPage, ellipsis: item === '...' }"
        :disabled="item === '...'"
        @click="onPageClick(item)"
      >
        {{ item }}
      </button>

      <ui-button
        size="sm"
        variant="secondary"
        :disabled="currentPage >= totalPages"
        @click="emit('update:modelValue', currentPage + 1)"
      >
        Next
      </ui-button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiButton from './UiButton.vue'

type PaginationItem = number | '...'

interface Props {
  modelValue: number
  totalItems: number
  pageSize: number
  maxVisible?: number
  showSummary?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  maxVisible: 5,
  showSummary: true,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
}>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.totalItems / Math.max(props.pageSize, 1))))
const currentPage = computed(() => Math.min(Math.max(props.modelValue, 1), totalPages.value))

const fromItem = computed(() => {
  if (!props.totalItems) return 0
  return (currentPage.value - 1) * props.pageSize + 1
})

const toItem = computed(() => {
  if (!props.totalItems) return 0
  return Math.min(currentPage.value * props.pageSize, props.totalItems)
})

const pageItems = computed<PaginationItem[]>(() => {
  const total = totalPages.value
  const maxVisible = Math.max(3, props.maxVisible)

  if (total <= maxVisible) {
    return Array.from({ length: total }, (_, index) => index + 1)
  }

  const middleSlots = maxVisible - 2
  let start = Math.max(2, currentPage.value - Math.floor(middleSlots / 2))
  const end = Math.min(total - 1, start + middleSlots - 1)
  start = Math.max(2, end - middleSlots + 1)

  const items: PaginationItem[] = [1]

  if (start > 2) items.push('...')
  for (let page = start; page <= end; page += 1) items.push(page)
  if (end < total - 1) items.push('...')

  items.push(total)
  return items
})

function onPageClick(item: PaginationItem) {
  if (item === '...') return
  emit('update:modelValue', item)
}
</script>

<style scoped>
.pagination {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 0.8rem;
  padding-top: 12px;
}

.summary {
  grid-column: 1;
  justify-self: start;
  color: var(--muted-foreground);
  font-size: 0.92rem;
}

.controls {
  grid-column: 2;
  justify-self: center;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  justify-content: center;
}

.page-pill {
  min-width: 2rem;
  height: 2rem;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--foreground);
  font-weight: 700;
  cursor: pointer;
  padding: 0 0.5rem;
}

.page-pill:hover:not(:disabled) {
  border-color: var(--primary);
}

.page-pill.active {
  background: var(--primary);
  color: var(--primary-foreground);
  border-color: var(--primary);
}

.page-pill.ellipsis {
  cursor: default;
  opacity: 0.7;
}

.page-pill:disabled {
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .pagination {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex-wrap: wrap;
  }

  .controls {
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>
