<template>
  <div
    class="query-field"
    :class="{ 'is-background-fetching': !isLoading && isFetching }"
    :aria-busy="!isLoading && isFetching ? true : undefined"
  >
    <slot v-if="isLoading && $slots.skeleton" name="skeleton" />
    <slot v-else />
  </div>
</template>

<script setup lang="ts">
import { computed, inject } from 'vue'
import { queryContextKey } from './queryContext'

interface Props {
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), { loading: undefined })
const queryContext = inject(queryContextKey, null)

const isLoading = computed(() => props.loading ?? queryContext?.isInitialLoading.value ?? false)
const isFetching = computed(() => queryContext?.isFetching.value ?? false)
</script>

<style scoped>
.query-field {
  display: contents;
}

.query-field.is-background-fetching :deep(> *) {
  opacity: 0.6;
  transition: opacity 0.18s ease;
}

@media (prefers-reduced-motion: reduce) {
  .query-field.is-background-fetching :deep(> *) {
    transition: none;
  }
}
</style>
