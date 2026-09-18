<template>
  <section class="admin-orders-page page-shell">
    <header class="admin-orders-hero">
      <div class="admin-orders-hero-copy">
        <div class="breadcrumb-label">
          <span>Admin</span>
          <span aria-hidden="true">/</span>
          <span>Shop Orders</span>
        </div>

        <h1 class="text-6xl">Shop Orders</h1>
        <p class="section-subtitle text-xl">
          Review, update statuses, and manage orders across all users.
        </p>
      </div>

      <div class="hero-actions">
        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="148px" height="45px" />
          </template>

          <ui-card variant="stat" class="admin-orders-stat-card">
            <span class="text-sm">Total orders:</span>
            <strong class="text-xl">{{ data?.count ?? 0 }}</strong>
          </ui-card>
        </ui-skeleton-loader>

        <ui-button variant="secondary" as-link to="/shop" size="lg">Back to Shop</ui-button>
      </div>
    </header>

    <div class="admin-orders-rule" aria-hidden="true"></div>

    <section class="admin-orders-section">
      <div class="toolbar">
        <ui-select v-model="statusFilter" :options="statusOptions" />
        <ui-input v-model="userFilter" placeholder="User id" />
      </div>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-skeleton v-for="i in 6" :key="i" variant="rect" width="100%" />
        </template>

        <p v-if="isLoadingError" class="text-muted">
          Failed to load orders ({{ error?.message || error?.code }})
        </p>
        <p v-else-if="!orders.length" class="text-muted">No orders found.</p>

        <table v-else class="orders-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>User</th>
              <th>Product</th>
              <th>Qty</th>
              <th>Total</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.id">
              <td>#{{ order.id }}</td>
              <td>
                <router-link :to="`/users/${order.user.id}`" class="profile-link">{{
                  order.user.username
                }}</router-link>
              </td>
              <td>{{ order.product.name }}</td>
              <td>{{ order.quantity }}</td>
              <td>{{ order.total_cost }}</td>
              <td>{{ order.status }}</td>
              <td>
                <div class="actions">
                  <ui-select
                    :model-value="order.status"
                    :options="mutableStatusOptions"
                    @update:model-value="(value) => changeStatus(order.id, value as any)"
                  />
                  <ui-button
                    size="sm"
                    variant="danger"
                    :disabled="!canCancel(order.status) || isCancelling"
                    @click="cancel(order.id)"
                  >
                    Cancel
                  </ui-button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <ui-pagination
          v-if="totalPages > 1"
          v-model="page"
          :total-items="orders.length"
          :page-size="pageSize"
          :show-summary="false"
        />
      </ui-skeleton-loader>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiPagination from '@/components/ui/UiPagination.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useNotification } from '@/composables/useNotification'
import type { ShopOrderStatus } from '@/api/services/shop/types'
import { useCancelAdminOrder, useListAdminOrders, useUpdateAdminOrderStatus } from '@/api/shop/shop'

const { showNotification } = useNotification()
const page = ref(1)
const pageSize = ref(20)
const statusFilter = ref('all')
const userFilter = ref('')

watch([statusFilter, userFilter], () => {
  page.value = 1
})

// TODO: add "all" option to backend
const { data, isLoading, isLoadingError, error } = useListAdminOrders(
  computed(() => ({
    page: page.value,
    page_size: pageSize.value,
    status: statusFilter.value === 'all' ? '' : statusFilter.value,
    user: userFilter.value || undefined,
  })),
)
const { mutate: updateStatus } = useUpdateAdminOrderStatus()
const { mutate: cancelOrder, isPending: isCancelling } = useCancelAdminOrder()

const orders = computed(() => data.value?.results ?? [])
const totalPages = computed(() => Math.max(1, Math.ceil((data.value?.count || 0) / pageSize.value)))

const statusOptions = [
  { value: 'all', label: 'All statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'shipped', label: 'Shipped' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
]

const mutableStatusOptions = [
  { value: 'pending', label: 'Pending' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'shipped', label: 'Shipped' },
  { value: 'completed', label: 'Completed' },
]

const canCancel = (status: ShopOrderStatus) => ['pending', 'confirmed'].includes(status)

const changeStatus = (
  orderId: number,
  status: 'pending' | 'confirmed' | 'shipped' | 'completed',
) => {
  updateStatus(
    { orderId, data: { status } },
    {
      onSuccess: () => showNotification('Order status updated.', 'success'),
      onError: (error) => showNotification(error?.message, 'error'),
    },
  )
}

const cancel = (orderId: number) => {
  cancelOrder(
    { orderId },
    {
      onSuccess: () => showNotification('Order cancelled.', 'success'),
      onError: (error) => showNotification(error?.message, 'error'),
    },
  )
}
</script>

<style scoped>
.admin-orders-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.admin-orders-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.admin-orders-hero-copy {
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

.admin-orders-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.admin-orders-hero .section-subtitle {
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

.admin-orders-stat-card {
  display: flex;
}

.admin-orders-stat-card strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.admin-orders-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.admin-orders-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.admin-orders-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.toolbar {
  display: grid;
  grid-template-columns: 220px 220px;
  gap: 8px;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
}

.orders-table th,
.orders-table td {
  border-bottom: 1px solid var(--border);
  padding: 8px;
  text-align: left;
  vertical-align: top;
}

.actions {
  display: grid;
  gap: 6px;
  min-width: 170px;
}

.profile-link {
  color: var(--brand-700);
  font-weight: 700;
  text-decoration: none;
}

.pagination {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

@media (max-width: 960px) {
  .toolbar {
    grid-template-columns: 1fr;
  }

  .orders-table {
    display: block;
    overflow-x: auto;
  }
}

@media (max-width: 760px) {
  .admin-orders-page {
    padding: 1rem 1rem 2rem;
  }

  .admin-orders-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .admin-orders-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .admin-orders-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }
}
</style>
