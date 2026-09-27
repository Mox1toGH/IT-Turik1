<template>
  <PaginationRoot
    class="pagination"
    aria-label="Pagination"
    :page="currentPage"
    :total="totalItems"
    :items-per-page="pageSize"
    :sibling-count="siblingCount"
    show-edges
    @update:page="(value) => emit('update:modelValue', value)"
  >
    <div v-if="showSummary" class="summary">
      Showing {{ fromItem }}-{{ toItem }} of {{ totalItems }}
    </div>

    <PaginationList v-slot="{ items }" class="controls">
      <PaginationPrev as-child>
        <ui-button size="sm" variant="secondary" :disabled="currentPage <= 1">Prev</ui-button>
      </PaginationPrev>

      <template
        v-for="(item, index) in items"
        :key="item.type === 'page' ? `page-${item.value}` : `ellipsis-${index}`"
      >
        <PaginationListItem v-if="item.type === 'page'" v-bind="item" class="page-pill">
          {{ item.value }}
        </PaginationListItem>
        <PaginationEllipsis v-else :index="index" class="page-pill ellipsis">
          ...
        </PaginationEllipsis>
      </template>

      <PaginationNext as-child>
        <ui-button size="sm" variant="secondary" :disabled="currentPage >= totalPages"
          >Next</ui-button
        >
      </PaginationNext>
    </PaginationList>
  </PaginationRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  PaginationRoot,
  PaginationList,
  PaginationListItem,
  PaginationEllipsis,
  PaginationPrev,
  PaginationNext,
} from 'reka-ui'
import UiButton from './UiButton.vue'

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

const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.totalItems / Math.max(props.pageSize, 1))),
)
const currentPage = computed(() => Math.min(Math.max(props.modelValue, 1), totalPages.value))

const siblingCount = computed(() =>
  Math.max(1, Math.floor((Math.max(3, props.maxVisible) - 3) / 2)),
)

const fromItem = computed(() => {
  if (!props.totalItems) return 0
  return (currentPage.value - 1) * props.pageSize + 1
})

const toItem = computed(() => {
  if (!props.totalItems) return 0
  return Math.min(currentPage.value * props.pageSize, props.totalItems)
})
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

.page-pill[data-selected] {
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
