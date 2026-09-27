<template>
  <ui-card class="product-card" :class="{ unavailable: !product.is_available }">
    <template #header>
      <div class="card-head">
        <strong class="product-title" :title="product.name">
          {{ truncateText(product.name, 100) }}
        </strong>
        <ui-badge :variant="product.is_available ? 'green' : 'gray'">
          {{ product.is_available ? 'Available' : 'Out of stock' }}
        </ui-badge>
      </div>
    </template>

    <img
      v-if="image"
      :src="image"
      class="thumb"
      alt="Product image"
      @click="emit('preview', image)"
    />

    <p class="price">{{ product.price }} pts</p>
    <p class="meta">{{ product.category.name }} | {{ product.product_type }}</p>
    <p class="desc" :title="product.description">
      {{ truncateText(product.description || 'No description', 150) }}
    </p>

    <div class="card-actions">
      <ui-button size="md" @click="emit('view', product)">Buy</ui-button>
      <ui-button v-if="isAdmin" variant="secondary" size="sm" @click="emit('edit', product)"
        >Edit</ui-button
      >
      <ui-button v-if="isAdmin" size="sm" variant="danger" @click="emit('delete', product)">
        Delete
      </ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { getProductImage } from '../../lib/getProductImage'
import { truncateText } from '@/lib/utils'
import type { Product } from '@/api/.ts.schemas'

const props = defineProps<{
  product: Product
  isAdmin?: boolean
}>()

const emit = defineEmits<{
  view: [product: Product]
  edit: [product: Product]
  delete: [product: Product]
  preview: [url: string]
}>()

const image = computed(() => getProductImage(props.product))
</script>

<style scoped>
.product-card {
  background: var(--muted);
}
.product-card.unavailable {
  filter: grayscale(1);
  opacity: 0.7;
}
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.product-title {
  min-width: 0;
  overflow-wrap: anywhere;
  word-break: break-word;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}
.thumb {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 8px;
  cursor: zoom-in;
}
.price {
  margin: 6px 0 0;
  font-weight: 700;
}
.meta {
  margin: 2px 0;
  color: var(--muted-foreground);
  font-size: 0.85rem;
}
.desc {
  margin: 4px 0;
  font-size: 0.9rem;
  color: var(--muted-foreground);
}
.card-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: auto;
}
</style>
