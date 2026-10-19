<template>
  <div :class="['query-state', { 'is-fetching': isFetching && status === 'data' }]">
    <div v-if="isStale && status === 'data'" class="stale-banner" role="status">
      <span>Update failed</span>
      <ui-button variant="link" :disabled="isFetching" @click="handleRetry">
        {{ isFetching ? 'Retrying…' : 'Retry' }}
      </ui-button>
    </div>

    <Transition name="skeleton-fade" mode="out-in">
      <div :key="status === 'loading' ? 'skeleton' : 'content'" class="query-state__content">
        <div
          v-if="status === 'loading'"
          class="query-state__block"
          aria-busy="true"
          aria-live="polite"
        >
          <slot name="skeleton">
            <ui-skeleton height="18px" />
            <ui-skeleton height="18px" />
            <ui-skeleton height="18px" />
          </slot>
        </div>

        <div v-else-if="status === 'error'" class="query-state__block">
          <div v-if="$slots.error" role="alert">
            <slot
              name="error"
              :errorCode="errorCode"
              :isFetching="isFetching"
              :retry="handleRetry"
            />
          </div>
          <p v-else-if="errorCode === 'network' && !isOnline" class="query-state__muted">
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

        <div v-else-if="status === 'empty'" class="query-state__block query-state__empty">
          <slot name="empty">
            <p class="query-state__muted">{{ emptyText ?? 'Nothing here yet.' }}</p>
          </slot>
          <slot name="empty-action" />
        </div>

        <div v-else :class="{ dimmed: isFetching }" :aria-busy="isFetching || undefined">
          <ui-error-boundary>
            <slot />
          </ui-error-boundary>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiButton from '@/components/ui/UiButton'
import UiCardError from '@/components/ui/UiCardError'
import UiErrorBoundary from '@/components/ui/UiErrorBoundary'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useConnection } from '@/composables/useConnection'
import { useQueryState, type EmptyPredicate, type QueryLike } from '@/composables/useQueryState'

interface Props {
  /** Complete result returned by a Vue Query query composable. */
  query: QueryLike
  /** Subject name used in the default error copy, e.g. `teams`. */
  title?: string
  emptyText?: string
  /**
   * Overrides how resolved data is classified as empty.
   *
   * Pass a predicate to replace the built-in heuristic, or `true` / `false` to
   * force the empty state on or off. Omit it to use the default shapes:
   * empty arrays, `{ total: 0 }`, `{ items: [] }`, `{ results: [] }`.
   */
  isEmpty?: boolean | EmptyPredicate
}

// `isEmpty: undefined` keeps an absent boolean prop from being cast to `false`,
// so omitting `:is-empty` still uses the default heuristic.
const props = withDefaults(defineProps<Props>(), {
  isEmpty: undefined,
})

const { isOnline } = useConnection()

const { status, errorCode, isStale, isFetching, refetch } = useQueryState(
  computed(() => props.query),
  () => ({ isEmpty: props.isEmpty }),
)

function handleRetry() {
  refetch()
}
</script>

<style scoped>
.query-state {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.query-state__content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.query-state__block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.query-state__empty {
  align-items: center;
  text-align: center;
  padding: 1rem 0;
}
.query-state__muted {
  margin: 0;
  font-size: 0.9rem;
  color: var(--muted-foreground);
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
  border-radius: 8px;
  background: var(--muted);
  color: var(--muted-foreground);
  font-size: 0.8rem;
}
.stale-banner :deep(.link-btn) {
  color: inherit;
}

.skeleton-fade-enter-active {
  transition: opacity 0.2s ease;
}
.skeleton-fade-leave-active {
  transition: opacity 0.1s ease;
}
.skeleton-fade-enter-from {
  opacity: 0;
}
.skeleton-fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .dimmed > * {
    opacity: 0.75;
  }
}
</style>
