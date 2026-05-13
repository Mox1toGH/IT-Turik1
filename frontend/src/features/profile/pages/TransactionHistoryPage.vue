<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">Transactions</p>
            <h1 class="section-title">
              {{ isAdminUserView ? `User #${targetUserId} transaction history` : 'My transaction history' }}
            </h1>
          </div>
          <div class="head-actions">
            <ui-button variant="secondary" @click="goBack">Back</ui-button>
          </div>
        </div>
      </template>

      <div class="toolbar">
        <label class="toolbar-field">
          <span class="toolbar-label">Sort by</span>
          <ui-select v-model="ordering" :options="orderingOptions" min-width="220px" />
        </label>
      </div>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div style="display: grid; gap: 8px">
            <ui-skeleton v-for="i in 6" :key="i" variant="rect" width="100%" />
          </div>
        </template>

        <p v-if="isLoadingError" class="text-muted">
          Failed to load transactions ({{ error?.message || error?.code || 'unknown' }}).
        </p>

        <p v-else-if="!transactions?.results?.length" class="text-muted">No transactions yet.</p>

        <div v-else class="list">
          <ui-card v-for="tx in transactions.results" :key="tx.id" class="tx-card">
            <template #header>
              <div class="tx-head">
                <strong :class="['tx-amount', tx.amount >= 0 ? 'positive' : 'negative']">
                  {{ tx.amount >= 0 ? '+' : '' }}{{ tx.amount }}
                </strong>
                <span class="meta">{{ formatDateTime(tx.created_at) }}</span>
              </div>
            </template>

            <p class="tx-reason">{{ tx.reason }}</p>
          </ui-card>

          <div v-if="totalPages > 1" class="pagination">
            <ui-button variant="secondary" :disabled="currentPage === 1" @click="prevPage">Prev</ui-button>
            <span class="page-info">Page {{ currentPage }} / {{ totalPages }}</span>
            <ui-button variant="secondary" :disabled="currentPage === totalPages" @click="nextPage">Next</ui-button>
          </div>
        </div>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { parseApiError } from '@/api/errors'
import { useProfile } from '@/api/queries/accounts'
import { useAdminUserPointsTransactions, useMyPointsTransactions } from '@/api/queries/points'
import type { PointsOrdering } from '@/api/services/points/types'

const route = useRoute()
const router = useRouter()
const { data: viewer } = useProfile()

const currentPage = ref(1)
const pageSize = ref(20)
const ordering = ref<PointsOrdering>('-created_at')

const targetUserId = computed(() => Number(route.params.id || 0))
const isAdminUserView = computed(() => viewer.value?.role === 'admin' && !!targetUserId.value)

const myQuery = useMyPointsTransactions(
  { page: currentPage, pageSize, ordering },
  { enabled: computed(() => !isAdminUserView.value) },
)

const adminQuery = useAdminUserPointsTransactions(
  targetUserId,
  { page: currentPage, pageSize, ordering },
  { enabled: isAdminUserView },
)

const isLoading = computed(() => (isAdminUserView.value ? adminQuery.isLoading.value : myQuery.isLoading.value))
const isLoadingError = computed(() =>
  isAdminUserView.value ? adminQuery.isLoadingError.value : myQuery.isLoadingError.value,
)
const rawError = computed(() => (isAdminUserView.value ? adminQuery.error.value : myQuery.error.value))
const error = computed(() => parseApiError(rawError.value))
const transactions = computed(() =>
  isAdminUserView.value ? adminQuery.data.value : myQuery.data.value,
)

const totalPages = computed(() => {
  const total = transactions.value?.count || 0
  return Math.max(1, Math.ceil(total / pageSize.value))
})

const orderingOptions: Array<{ value: PointsOrdering; label: string }> = [
  { value: '-created_at', label: 'Date: newest first' },
  { value: 'created_at', label: 'Date: oldest first' },
  { value: '-amount', label: 'Amount: high to low' },
  { value: 'amount', label: 'Amount: low to high' },
]

const formatDateTime = (value: string) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('uk-UA')
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value -= 1
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value += 1
}

const goBack = () => {
  if (isAdminUserView.value) {
    router.push(`/users/${targetUserId.value}`)
    return
  }
  router.push('/profile')
}
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.head-actions {
  display: flex;
  gap: 8px;
}

.toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.toolbar-field {
  display: grid;
  gap: 4px;
}

.toolbar-label {
  font-size: 0.8rem;
  color: var(--color-gray-500);
  font-weight: 600;
}

.list {
  display: grid;
  gap: 10px;
}

.tx-card {
  background: var(--muted);
  color: var(--muted-foreground);
}

.tx-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
}

.tx-amount {
  font-size: 1.05rem;
}

.tx-amount.positive {
  color: #1a8b3a;
}

.tx-amount.negative {
  color: var(--destructive);
}

.meta {
  color: var(--color-gray-500);
  font-size: 0.86rem;
}

.tx-reason {
  margin: 0;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 8px;
}

.page-info {
  font-weight: 600;
  color: var(--color-gray-600);
}

@media (max-width: 760px) {
  .head {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar {
    justify-content: flex-start;
  }
}
</style>
