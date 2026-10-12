<template>
  <div v-if="!isOnline" class="offline-banner" role="alert">
    <span class="offline-banner__text">No connection</span>
    <ui-button size="sm" variant="secondary" :disabled="isRefetching" @click="retryFailed">
      {{ isRefetching ? 'Retrying…' : 'Try again' }}
    </ui-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import { useConnection } from '@/composables/useConnection'
import { queryClient } from '@/lib/queryClient'

const { isOnline } = useConnection()
const isRefetching = ref(false)

async function retryFailed() {
  isRefetching.value = true
  try {
    await queryClient.refetchQueries({
      type: 'active',
      predicate: (q) => q.state.status === 'error',
    })
  } finally {
    isRefetching.value = false
  }
}
</script>

<style scoped>
.offline-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--muted);
  color: var(--foreground);
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.6rem 0.9rem;
  margin-bottom: 1rem;
}
</style>
