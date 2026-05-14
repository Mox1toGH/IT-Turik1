<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">Shop</p>
            <h1 class="section-title">My Orders</h1>
          </div>
          <ui-button variant="secondary" as-link to="/profile">Back to Profile</ui-button>
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-skeleton v-for="i in 5" :key="i" variant="rect" width="100%" />
        </template>

        <p v-if="isLoadingError" class="text-muted">Failed to load orders ({{ parsedError?.message || parsedError?.code }})</p>
        <p v-else-if="!orders.length" class="text-muted">No orders yet.</p>

        <div v-else class="list">
          <ui-card v-for="order in orders" :key="order.id" class="order-card">
            <template #header>
              <div class="order-head">
                <strong>#{{ order.id }} · {{ order.product.name }}</strong>
                <ui-badge>{{ order.status }}</ui-badge>
              </div>
            </template>

            <p>Quantity: {{ order.quantity }}</p>
            <p>Total: {{ order.total_cost }} points</p>
            <p>Date: {{ formatDate(order.created_at) }}</p>

            <router-link v-if="transactionsByOrder[order.id]" :to="`/profile/points`" class="tx-link">
              Open related points transaction #{{ transactionsByOrder[order.id]?.id }}
            </router-link>

            <ui-button
              v-if="canCancel(order.status)"
              size="sm"
              variant="danger"
              :disabled="isCancelling"
              @click="cancel(order.id)"
            >
              Cancel Order
            </ui-button>
          </ui-card>

          <div v-if="totalPages > 1" class="pagination">
            <ui-button variant="secondary" :disabled="page === 1" @click="page -= 1">Prev</ui-button>
            <span>Page {{ page }} / {{ totalPages }}</span>
            <ui-button variant="secondary" :disabled="page === totalPages" @click="page += 1">Next</ui-button>
          </div>
        </div>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { parseApiError } from '@/api/errors'
import { useCancelMyShopOrder, useMyShopOrders } from '@/api/queries/shop'
import { useMyPointsTransactions } from '@/api/queries/points'
import { useNotification } from '@/composables/useNotification'
import type { ShopOrderStatus } from '@/api/services/shop/types'

const { showNotification } = useNotification()
const page = ref(1)
const pageSize = ref(12)

const { data, isLoading, isLoadingError, error } = useMyShopOrders(
  computed(() => ({ page: page.value, page_size: pageSize.value })),
)
const { data: txData } = useMyPointsTransactions({ page: 1, page_size: 100, ordering: '-created_at' })
const { mutate: cancelOrder, isPending: isCancelling } = useCancelMyShopOrder()

const parsedError = computed(() => parseApiError(error.value))
const orders = computed(() => data.value?.results ?? [])
const totalPages = computed(() => Math.max(1, Math.ceil((data.value?.count || 0) / pageSize.value)))

const transactionsByOrder = computed<Record<number, { id: number }>>(() => {
  const map: Record<number, { id: number }> = {}
  for (const tx of txData.value?.results ?? []) {
    if (tx.order_id) map[tx.order_id] = { id: tx.id }
  }
  return map
})

const canCancel = (status: ShopOrderStatus) => ['pending', 'confirmed'].includes(status)

const cancel = (orderId: number) => {
  cancelOrder(
    { orderId },
    {
      onSuccess: () => showNotification('Order cancelled.', 'success'),
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    },
  )
}

const formatDate = (value: string) => new Date(value).toLocaleString('uk-UA')
</script>

<style scoped>
.head { display: flex; justify-content: space-between; gap: 10px; align-items: center; }
.list { display: grid; gap: 10px; }
.order-card { background: var(--muted); }
.order-head { display: flex; justify-content: space-between; gap: 8px; align-items: center; }
.tx-link { color: var(--brand-700); font-weight: 700; text-decoration: none; }
.pagination { margin-top: 12px; display: flex; gap: 8px; justify-content: center; align-items: center; }
@media (max-width: 760px) { .head { flex-direction: column; align-items: flex-start; } }
</style>
