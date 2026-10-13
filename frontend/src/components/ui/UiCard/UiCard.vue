<template>
  <section
    :class="[
      'card',
      `card-${variant}`,
      { scrollable, 'is-fetching': isFetching && status === 'data' },
    ]"
  >
    <header v-if="$slots.header || title" class="card-header">
      <slot name="header">
        <h3 class="card-title">{{ title }}</h3>
        <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
      </slot>
    </header>

    <div class="card-body">
      <div v-if="isStale && status === 'data'" class="stale-banner" role="status">
        <span>Update failed</span>
        <button type="button" :disabled="isFetching" @click="handleRetry">
          {{ isFetching ? 'Retrying…' : 'Retry' }}
        </button>
      </div>

      <div v-if="status === 'loading'" class="card-state" aria-busy="true" aria-live="polite">
        <slot name="skeleton">
          <ui-skeleton height="18px" />
          <ui-skeleton height="18px" />
          <ui-skeleton height="18px" />
        </slot>
      </div>

      <div v-else-if="status === 'error'" class="card-state">
        <div v-if="$slots.error" role="alert"><slot name="error" /></div>
        <p v-else-if="errorCode === 'network' && !isOnline" class="card-muted">
          Waiting for connection…
        </p>
        <ui-card-error
          v-else
          :title="title"
          :error-code="errorCode"
          :is-fetching="isFetching"
          @retry="handleRetry"
        />
      </div>

      <div v-else-if="status === 'empty'" class="card-state card-empty">
        <p class="card-muted">{{ emptyText ?? 'Nothing here yet.' }}</p>
        <slot name="empty-action" />
      </div>

      <div v-else :class="{ dimmed: isFetching }" :aria-busy="isFetching || undefined">
        <ui-error-boundary>
          <slot />
        </ui-error-boundary>
      </div>
    </div>

    <footer v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed, toRefs } from 'vue'
import UiCardError from '@/components/ui/UiCardError'
import UiErrorBoundary from '@/components/ui/UiErrorBoundary'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useConnection } from '@/composables/useConnection'
import {
  useCardState,
  type CardErrorCode,
  type CardQuery,
  type CardStatus,
} from '@/composables/useCardState'

interface Props {
  title?: string
  subtitle?: string
  query?: CardQuery
  status?: CardStatus
  isFetching?: boolean
  isStale?: boolean
  errorCode?: CardErrorCode
  emptyText?: string
  scrollable?: boolean
  variant?: 'default' | 'panel' | 'stat' | 'hero' | 'form' | 'inset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  status: 'data',
  isFetching: false,
  isStale: false,
  errorCode: null,
})
const emit = defineEmits<{ (e: 'retry'): void }>()

const { title, subtitle, emptyText, scrollable, variant } = toRefs(props)
const { isOnline } = useConnection()

const q = useCardState(
  computed<CardQuery>(
    () => props.query ?? { isPending: false, isError: false, data: null, error: null },
  ),
)

const fromQuery = computed(() => props.query !== undefined)
const status = computed<CardStatus>(() => (fromQuery.value ? q.status.value : props.status))
const errorCode = computed<CardErrorCode>(() =>
  fromQuery.value ? q.errorCode.value : props.errorCode,
)
const isStale = computed(() => (fromQuery.value ? q.isStale.value : props.isStale))
const isFetching = computed(() => (fromQuery.value ? q.isFetching.value : props.isFetching))

const handleRetry = () => (fromQuery.value ? q.refetch() : emit('retry'))
</script>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.2rem;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--card);
  color: var(--card-foreground);
  box-shadow: 0 5px 20px rgb(0 0 0 / 0.05);
}
.dark .card {
  box-shadow: 0 5px 20px rgb(0 0 0 / 0.25);
}

.card-panel {
  gap: 1.7rem;
  padding: 2.4rem 2rem 1.8rem;
  border-color: var(--line-soft);
  border-radius: 20px;
}
.card-stat {
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  min-width: 100px;
  padding: 0.5rem 1.1rem;
  border-color: var(--line-soft);
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
}
.card-inset {
  padding: 0.8rem;
  border-color: var(--line-soft);
  border-radius: 12px;
  background: color-mix(in srgb, var(--card) 92%, var(--foreground) 8%);
}

.card-title {
  margin: 0;
  font-size: 1rem;
}
.card-subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.85rem;
  color: var(--muted-foreground);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.card.scrollable {
  max-height: calc(100vh - 32px);
}
.card.scrollable > .card-body {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
}

.card-state {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.card-empty {
  align-items: center;
  text-align: center;
  padding: 1rem 0;
}
.card-muted {
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
.stale-banner button {
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  font-weight: 600;
  text-decoration: underline;
  cursor: pointer;
}
.stale-banner button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
.stale-banner button:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}

@media (max-width: 700px) {
  .card-panel {
    padding: 1.4rem;
  }
}
@media (prefers-reduced-motion: reduce) {
  .dimmed > * {
    opacity: 0.75;
  }
}
</style>
