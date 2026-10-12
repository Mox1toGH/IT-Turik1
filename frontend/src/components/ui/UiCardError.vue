<template>
  <div class="card-error" role="alert">
    <component :is="IconComponent" class="card-error__icon" aria-hidden="true" />
    <p class="card-error__title">{{ title }}</p>
    <p class="card-error__hint text-muted">{{ hint }}</p>
    <ui-button
      v-if="showRetry"
      size="sm"
      variant="secondary"
      :disabled="isFetching"
      @click="emit('retry')"
    >
      {{ isFetching ? 'Retrying…' : 'Try again' }}
    </ui-button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { TriangleAlert, CloudOff } from 'lucide-vue-next'
import UiButton from '@/components/ui/UiButton'
import type { CardErrorCode } from '@/composables/useCardState'

interface Props {
  errorCode?: CardErrorCode
  title?: string
  isFetching?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  errorCode: null,
  title: '',
  isFetching: false,
})

const emit = defineEmits<{
  (e: 'retry'): void
}>()

const code = computed(() => props.errorCode)

const IconComponent = computed(() => (code.value === 'network' ? CloudOff : TriangleAlert))

const showRetry = computed(() => code.value !== 403 && code.value !== 404)

const title = computed(() => {
  if (code.value === 'network') return 'No connection'
  if (typeof code.value === 'number' && code.value >= 500) return 'Server unavailable'
  if (code.value === 403) return 'No access'
  if (code.value === 404) return 'Not found'
  if (props.title) return `Couldn't load ${props.title}`
  return "Couldn't load data"
})

const hint = computed(() => {
  if (code.value === 'network') return 'Check your internet and try again.'
  if (typeof code.value === 'number' && code.value >= 500)
    return 'Something broke on our side. Try again in a moment.'
  if (code.value === 403) return "You don't have permission to view this."
  if (code.value === 404) return 'This data no longer exists.'
  return 'Try again.'
})
</script>

<style scoped>
.card-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 0.35rem;
  padding: 1.5rem 1rem;
}

.card-error__icon {
  width: 22px;
  height: 22px;
  color: var(--muted-foreground);
}

.card-error__title {
  font-weight: 700;
  margin: 0;
}

.card-error__hint {
  margin: 0 0 0.5rem;
  font-size: 0.85rem;
}

@media (prefers-reduced-motion: reduce) {
  .card-error {
    scroll-behavior: auto;
  }
}
</style>
