<template>
  <div
    :class="[
      'card',
      variantClass,
      {
        scrollable: props.scrollable,
        'is-fetching': effectiveIsFetching && effectiveStatus === 'data',
      },
    ]"
  >
    <div class="card-head">
      <slot v-if="$slots.header" name="header" />
      <div v-else-if="props.title" class="card-default-header">
        <div class="card-default-header__text">
          <h3 class="card-default-header__title">{{ props.title }}</h3>
          <p v-if="props.subtitle" class="card-default-header__subtitle text-muted">
            {{ props.subtitle }}
          </p>
        </div>

        <div v-if="$slots.controls" class="card-default-header__controls">
          <slot name="controls" />
        </div>

        <div v-if="$slots.badge && effectiveStatus === 'data'" class="card-default-header__badge">
          <slot name="badge" />
        </div>
      </div>

      <div v-else-if="$slots.badge && effectiveStatus === 'data'" class="card-badge-row">
        <slot name="badge" />
      </div>
    </div>

    <div class="card-body">
      <div
        v-if="effectiveIsStale && effectiveStatus === 'data'"
        class="stale-banner"
        role="status"
      >
        <span>Update failed</span>
        <button
          type="button"
          class="stale-banner__retry"
          :disabled="effectiveIsFetching"
          @click="handleRetry"
        >
          {{ effectiveIsFetching ? 'Retrying…' : 'Retry' }}
        </button>
      </div>

      <div
        v-if="effectiveStatus === 'loading'"
        class="card-status-block"
        aria-busy="true"
        aria-live="polite"
      >
        <slot name="skeleton">
          <ui-skeleton height="18px" />
          <ui-skeleton height="18px" />
          <ui-skeleton height="18px" />
        </slot>
      </div>

      <div v-else-if="effectiveStatus === 'error'" class="card-status-block">
        <div v-if="$slots.error" role="alert">
          <slot name="error" />
        </div>
        <p
          v-else-if="effectiveErrorCode === 'network' && !isOnline"
          class="card-empty__text text-muted"
        >
          Waiting for connection…
        </p>
        <ui-card-error
          v-else
          :title="props.title"
          :error-code="effectiveErrorCode"
          :is-fetching="effectiveIsFetching"
          @retry="handleRetry"
        />
      </div>

      <div v-else-if="effectiveStatus === 'empty'" class="card-status-block card-empty">
        <p class="card-empty__text text-muted">{{ props.emptyText ?? 'Nothing here yet.' }}</p>
        <slot name="empty-action" />
      </div>

      <div
        v-else
        :class="['card-data', { dimmed: effectiveIsFetching }]"
        :aria-busy="effectiveIsFetching || undefined"
      >
        <ui-error-boundary>
          <slot />
        </ui-error-boundary>
      </div>
    </div>

    <div v-if="$slots.footer" class="card-foot">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCardError from '@/components/ui/UiCardError.vue'
import UiErrorBoundary from '@/components/ui/UiErrorBoundary.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { useConnection } from '@/composables/useConnection'
import { useCardState, type CardErrorCode, type CardQuery, type CardStatus } from '@/composables/useCardState'

interface Props {
  title?: string
  subtitle?: string
  /** Primary query mode: the card derives status/error/retry from it. */
  query?: CardQuery
  /** Manual fallback mode (ignored when query is provided). */
  status?: CardStatus
  isFetching?: boolean
  isStale?: boolean
  errorCode?: CardErrorCode
  emptyText?: string
  scrollable?: boolean
  variant?: 'default' | 'panel' | 'stat' | 'hero' | 'form' | 'actions' | 'inset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  status: 'data',
  isFetching: false,
  isStale: false,
  errorCode: null,
})

const emit = defineEmits<{
  (e: 'retry'): void
}>()

const hasQuery = computed(() => props.query !== undefined)
const querySource = computed<CardQuery>(
  () => props.query ?? { isPending: false, isError: false, data: null, error: null },
)
const {
  status: queryStatus,
  errorCode: queryErrorCode,
  isStale: queryIsStale,
  isFetching: queryIsFetching,
  refetch: refetchQuery,
} = useCardState(querySource)

const effectiveStatus = computed<CardStatus>(() =>
  hasQuery.value ? queryStatus.value : props.status,
)
const effectiveErrorCode = computed<CardErrorCode>(() =>
  hasQuery.value ? queryErrorCode.value : props.errorCode,
)
const effectiveIsStale = computed(() => (hasQuery.value ? queryIsStale.value : props.isStale))
const effectiveIsFetching = computed(() =>
  hasQuery.value ? queryIsFetching.value : props.isFetching,
)

const handleRetry = () => {
  if (props.query) refetchQuery()
  else emit('retry')
}

const { isOnline } = useConnection()

const variantClass = computed(() => `card-${props.variant}`)
</script>

<style scoped>
.card {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: var(--card);
  color: var(--card-foreground);
  box-shadow: 0 5px 20px 0 rgb(0 0 0 / 0.05);
}

.dark .card {
  box-shadow: 0 5px 20px 0 rgb(0 0 0 / 0.25);
}

.card-panel {
  gap: 1.7rem;
  padding: 2.4rem 2rem 1.8rem;
  border-color: var(--line-soft);
  border-radius: 20px;
  background: var(--card);
}

.card-stat {
  min-width: 100px;
  min-height: 30px;
  padding: 0.5rem 1.1rem;
  align-items: center;
  justify-content: center;
  flex-direction: row;
  gap: 0.7rem;
  border-color: var(--line-soft);
  border-radius: 14px;
  background: var(--card);
}

.card-hero {
  padding: 1.5rem;
  border-color: var(--line-soft);
  border-radius: 20px;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--primary) 10%, transparent), transparent 44%),
    var(--card);
}

.card-form {
  gap: 1rem;
  padding: 1.25rem;
  border-color: var(--line-soft);
  border-radius: 18px;
  background: var(--card);
}

.card-actions {
  padding: 0.8rem;
  border-color: var(--line-soft);
  border-radius: 16px;
  background: color-mix(in srgb, var(--card) 92%, transparent);
  backdrop-filter: blur(12px);
}

.card-inset {
  padding: 0.8rem;
  border-color: var(--line-soft);
  border-radius: 12px;
  background: color-mix(in srgb, var(--card) 92%, var(--foreground) 8%);
}

.card-head,
.card-body,
.card-foot {
  display: contents;
}

.card.scrollable {
  max-height: calc(100vh - 16px * 2);
}

.card.scrollable > .card-body {
  display: block;
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
}

@media (max-width: 700px) {
  .card-panel {
    padding: 1.4rem;
  }
}

.error-fade-enter-active,
.error-fade-leave-active {
  transition: opacity 0.15s ease;
}

.error-fade-enter-from,
.error-fade-leave-to {
  opacity: 0;
}

.card-default-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.card-default-header__title {
  margin: 0;
  font-size: 1rem;
}

.card-default-header__subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.85rem;
}

.card-default-header__controls,
.card-default-header__badge,
.card-badge-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-status-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-empty {
  align-items: center;
  text-align: center;
  padding: 1rem 0;
}

.card-empty__text {
  margin: 0;
  font-size: 0.9rem;
}

.card-data {
  display: contents;
}

.card-data.dimmed > * {
  opacity: 0.6;
}

.stale-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--muted);
  color: var(--muted-foreground);
  font-size: 0.8rem;
  padding: 0.35rem 0.6rem;
}

.stale-banner__retry {
  font: inherit;
  font-size: 0.8rem;
  font-weight: 600;
  background: transparent;
  border: 0;
  cursor: pointer;
  color: inherit;
  text-decoration: underline;
  padding: 0;
}

.stale-banner__retry:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.stale-banner__retry:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}

.is-fetching {
  scroll-behavior: auto;
}

@media (prefers-reduced-motion: reduce) {
  .card-data.dimmed > * {
    opacity: 0.75;
  }
}
</style>
