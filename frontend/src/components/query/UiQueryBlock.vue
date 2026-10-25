<template>
  <div class="query-block">
    <div v-if="isStale" class="query-block__stale-banner" role="status">
      <span>Update failed</span>
      <ui-button variant="link" :disabled="isFetching" @click="handleRetry">
        {{ isFetching ? 'Retrying…' : 'Retry' }}
      </ui-button>
    </div>

    <div v-if="isInitialError" class="query-block__error" role="alert">
      <slot
        v-if="$slots.error"
        name="error"
        :error-code="errorCode"
        :is-fetching="isFetching"
        :retry="handleRetry"
      />
      <p v-else-if="errorCode === 'network' && !isOnline" class="query-block__muted">
        Waiting for connection…
      </p>
      <ui-card-error
        v-else
        :title="title ?? ''"
        :error-code="errorCode"
        :is-fetching="isFetching"
        @retry="handleRetry"
      />
    </div>

    <ui-error-boundary v-else>
      <slot />
    </ui-error-boundary>
  </div>
</template>

<script setup lang="ts">
import { computed, provide } from 'vue'
import UiButton from '@/components/ui/UiButton'
import UiCardError from '@/components/ui/UiCardError'
import UiErrorBoundary from '@/components/ui/UiErrorBoundary'
import { useConnection } from '@/composables/useConnection'
import { useQueryState, type QueryLike } from '@/composables/useQueryState'
import { queryContextKey } from './queryContext'

interface Props {
  query: QueryLike
  title?: string
}

const props = defineProps<Props>()

const { isOnline } = useConnection()
const { isInitialLoading, isError, data, errorCode, isFetching, refetch } = useQueryState(
  computed(() => props.query),
)

const isInitialError = computed(() => isError.value && data.value === undefined)
const isStale = computed(() => isError.value && data.value !== undefined)

provide(queryContextKey, { isInitialLoading, isFetching })

function handleRetry() {
  refetch()
}
</script>

<style scoped>
.query-block {
  display: contents;
}

.query-block__error,
.query-block__stale-banner {
  margin-block: 0.5rem;
}

.query-block__muted {
  margin: 0;
  font-size: 0.9rem;
  color: var(--muted-foreground);
}

.query-block__stale-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.35rem 0.6rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--muted);
  color: var(--muted-foreground);
  font-size: 0.8rem;
}

.query-block__stale-banner :deep(.link-btn) {
  color: inherit;
}
</style>
