<template>
  <div class="toolbar">
    <ui-input v-model="search" placeholder="Search by name" />
    <ui-select v-model="category" :options="categoryOptions" />
    <ui-select v-model="type" :options="typeOptions" />
    <ui-select v-model="ordering" :options="orderingOptions" />
  </div>
</template>

<script setup lang="ts">
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import {
  orderingOptions,
  typeOptions,
  type ProductOrdering,
  type ProductType,
} from '../../composables/useShopCatalog'

defineProps<{
  categoryOptions: { value: string; label: string }[]
}>()

const search = defineModel<string>('search', { default: '' })
const category = defineModel<string>('category', { default: 'all' })
const type = defineModel<ProductType>('type', { default: 'all' })
const ordering = defineModel<ProductOrdering>('ordering', { default: 'name' })
</script>

<style scoped>
.toolbar {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 12px;
}

@media (max-width: 900px) {
  .toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
