<template>
  <section class="orders-page page-shell">
    <header class="orders-hero">
      <div class="orders-hero-copy">
        <div class="breadcrumb-label">
          <span>Shop</span>
          <span aria-hidden="true">/</span>
          <span>My Orders</span>
        </div>

        <h1 class="text-6xl">My Orders</h1>
        <p class="section-subtitle text-xl">
          Track your purchases, statuses, and related points transactions.
        </p>
      </div>

      <div class="hero-actions">
        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="148px" height="45px" />
          </template>

          <ui-card variant="stat" class="orders-stat-card">
            <span class="text-sm">Total orders:</span>
            <strong class="text-xl">{{ data?.count ?? 0 }}</strong>
          </ui-card>
        </ui-skeleton-loader>
      </div>
    </header>

    <div class="orders-rule" aria-hidden="true"></div>

    <section class="orders-section">
      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-skeleton v-for="i in 5" :key="i" variant="rect" width="100%" />
        </template>

        <p v-if="isLoadingError" class="text-muted">
          Failed to load orders ({{ error?.message || error?.code }})
        </p>
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

            <router-link
              v-if="transactionsByOrder[order.id]"
              :to="`/profile/points`"
              class="tx-link"
            >
              Open related points transaction #{{ transactionsByOrder[order.id]?.id }}
            </router-link>

            <ui-button
              v-if="canCancel(order.status as ShopOrderStatus)"
              size="sm"
              variant="danger"
              :disabled="isCancelling"
              @click="cancel(order.id)"
            >
              Cancel Order
            </ui-button>
          </ui-card>

          <ui-pagination
            v-if="totalPages > 1"
            v-model="page"
            :total-items="orders.length"
            :page-size="pageSize"
            :show-summary="false"
          />
        </div>
      </ui-skeleton-loader>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiPagination from '@/components/ui/UiPagination.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { useNotification } from '@/composables/useNotification'
import type { ShopOrderStatus } from '@/api/services/shop/types'
import { useCancelMyOrder, useListMyOrders } from '@/api/shop/shop'
import { useListMyPointsTransactions } from '@/api/points/points'

const { showNotification } = useNotification()
const page = ref(1)
const pageSize = ref(12)

const { data, isLoading, isLoadingError, error } = useListMyOrders(
  computed(() => ({ page: page.value, page_size: pageSize.value })),
)
const { data: txData } = useListMyPointsTransactions({
  page: 1,
  page_size: 100,
  ordering: '-created_at',
})
const { mutate: cancelOrder, isPending: isCancelling } = useCancelMyOrder()

const orders = computed(() => data.value?.items ?? [])
const totalPages = computed(() => Math.max(1, Math.ceil((data.value?.count || 0) / pageSize.value)))

const transactionsByOrder = computed<Record<number, { id: number }>>(() => {
  const map: Record<number, { id: number }> = {}
  for (const tx of txData.value?.items ?? []) {
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
      onError: (error) => showNotification(error?.message, 'error'),
    },
  )
}

const formatDate = (value: string) => new Date(value).toLocaleString('uk-UA')
</script>

<style scoped>
.orders-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.orders-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.orders-hero-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.orders-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.orders-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

.orders-stat-card {
  display: flex;
}

.orders-stat-card strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.orders-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.orders-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.orders-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.list {
  display: grid;
  gap: 10px;
}

.order-card {
  background: var(--muted);
}

.order-head {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
}

.tx-link {
  color: var(--brand-700);
  font-weight: 700;
  text-decoration: none;
}

@media (max-width: 760px) {
  .orders-page {
    padding: 1rem 1rem 2rem;
  }

  .orders-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .orders-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .orders-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }
}
</style>
