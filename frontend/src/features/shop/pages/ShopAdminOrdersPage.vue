<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">Admin</p>
            <h1 class="section-title">Shop Orders</h1>
          </div>
          <ui-button variant="secondary" as-link to="/shop">Back to Shop</ui-button>
        </div>
      </template>

      <div class="toolbar">
        <ui-select v-model="statusFilter" :options="statusOptions" />
        <ui-input v-model="userFilter" placeholder="User id" />
      </div>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-skeleton v-for="i in 6" :key="i" variant="rect" width="100%" />
        </template>

        <p v-if="isLoadingError" class="text-muted">Failed to load orders ({{ parsedError?.message || parsedError?.code }})</p>
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
                <router-link :to="`/users/${order.user.id}`" class="profile-link">{{ order.user.username }}</router-link>
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

        <div v-if="totalPages > 1" class="pagination">
          <ui-button variant="secondary" :disabled="page === 1" @click="page -= 1">Prev</ui-button>
          <span>Page {{ page }} / {{ totalPages }}</span>
          <ui-button variant="secondary" :disabled="page === totalPages" @click="page += 1">Next</ui-button>
        </div>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { parseApiError } from '@/api/errors'
import { useAdminCancelOrder, useAdminShopOrders, useAdminUpdateOrderStatus } from '@/api/queries/shop'
import { useNotification } from '@/composables/useNotification'
import type { ShopOrderStatus } from '@/api/services/shop/types'

const { showNotification } = useNotification()
const page = ref(1)
const pageSize = ref(20)
const statusFilter = ref('')
const userFilter = ref('')

watch([statusFilter, userFilter], () => { page.value = 1 })

const { data, isLoading, isLoadingError, error } = useAdminShopOrders({
  page,
  pageSize,
  status: statusFilter,
  user: userFilter,
})
const { mutate: updateStatus } = useAdminUpdateOrderStatus()
const { mutate: cancelOrder, isPending: isCancelling } = useAdminCancelOrder()

const parsedError = computed(() => parseApiError(error.value))
const orders = computed(() => data.value?.results ?? [])
const totalPages = computed(() => Math.max(1, Math.ceil((data.value?.count || 0) / pageSize.value)))

const statusOptions = [
  { value: '', label: 'All statuses' },
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

const changeStatus = (orderId: number, status: 'pending' | 'confirmed' | 'shipped' | 'completed') => {
  updateStatus(
    { orderId, data: { status } },
    {
      onSuccess: () => showNotification('Order status updated.', 'success'),
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    },
  )
}

const cancel = (orderId: number) => {
  cancelOrder(
    { orderId },
    {
      onSuccess: () => showNotification('Order cancelled.', 'success'),
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    },
  )
}
</script>

<style scoped>
.head { display: flex; justify-content: space-between; gap: 10px; align-items: center; }
.toolbar { display: grid; grid-template-columns: 220px 220px; gap: 8px; margin-bottom: 12px; }
.orders-table { width: 100%; border-collapse: collapse; }
.orders-table th, .orders-table td { border-bottom: 1px solid var(--border); padding: 8px; text-align: left; vertical-align: top; }
.actions { display: grid; gap: 6px; min-width: 170px; }
.profile-link { color: var(--brand-700); font-weight: 700; text-decoration: none; }
.pagination { margin-top: 12px; display: flex; gap: 8px; justify-content: center; align-items: center; }
@media (max-width: 960px) {
  .toolbar { grid-template-columns: 1fr; }
  .orders-table { display: block; overflow-x: auto; }
  .head { flex-direction: column; align-items: flex-start; }
}
</style>
