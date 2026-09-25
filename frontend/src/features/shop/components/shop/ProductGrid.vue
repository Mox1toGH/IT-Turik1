<template>
  <ui-skeleton-loader :loading="isLoading">
    <template #skeleton>
      <div class="grid">
        <ui-card v-for="i in skeletonCount" :key="i">
          <ui-skeleton variant="rect" width="100%" height="120px" />
        </ui-card>
      </div>
    </template>

    <p v-if="isError" class="text-muted">Failed to load products ({{ errorMessage }})</p>
    <p v-else-if="!products.length" class="text-muted">No products found.</p>

    <div v-else class="grid">
      <product-card
        v-for="product in products"
        :key="product.id"
        :product="product"
        :is-admin="isAdmin"
        @view="emit('view', $event)"
        @edit="emit('edit', $event)"
        @delete="emit('delete', $event)"
        @preview="emit('preview', $event)"
      />
    </div>
  </ui-skeleton-loader>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import ProductCard from './ProductCard.vue'
import type { ProductResponse } from '@/api/backendAPINinja.schemas.ts'

withDefaults(
  defineProps<{
    products: ProductResponse[]
    isLoading?: boolean
    isError?: boolean
    errorMessage?: string
    isAdmin?: boolean
    skeletonCount?: number
  }>(),
  { isLoading: false, isError: false, errorMessage: '', isAdmin: false, skeletonCount: 6 },
)

const emit = defineEmits<{
  view: [product: ProductResponse]
  edit: [product: ProductResponse]
  delete: [product: ProductResponse]
  preview: [url: string]
}>()
</script>

<style scoped>
.grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
}
</style>
