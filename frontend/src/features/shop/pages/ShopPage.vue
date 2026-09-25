<template>
  <section class="page-shell shop-page">
    <section class="catalog-section">
      <shop-hero
        :total-products="totalCount"
        :is-loading="isLoading"
        :is-admin="isAdmin"
        @create-product="openProductCreate"
        @manage-categories="openCategoryModal"
      />

      <div class="shop-rule" aria-hidden="true"></div>

      <shop-toolbar
        v-model:search="search"
        v-model:category="selectedCategory"
        v-model:type="selectedType"
        v-model:ordering="selectedOrdering"
        :category-options="categoryOptions"
      />

      <product-grid
        :products="products"
        :is-loading="isLoading"
        :is-error="isLoadingError"
        :error-message="error?.message || error?.code"
        :is-admin="isAdmin"
        @view="openProductDetail"
        @edit="openProductEdit"
        @delete="openProductDelete"
        @preview="openImagePreview"
      />

      <ui-pagination
        v-if="totalPages > 1"
        v-model="currentPage"
        :total-items="totalCount"
        :page-size="pageSize"
        :show-summary="false"
      />
    </section>

    <product-detail-modal
      v-model="isDetailOpen"
      :product="selectedProduct"
      @preview="openImagePreview"
    />

    <product-editor-modal
      v-model="isProductEditOpen"
      :mode="selectedProduct ? 'edit' : 'create'"
      :product="selectedProduct"
      :categories="adminCategories"
      :avatar-frames="avatarFrames"
      :submitting="isSavingProduct"
      @submit="submitProductForm"
    />

    <ui-confirm-modal
      v-model="isProductDeleteOpen"
      title="Delete product"
      message="Delete this product?"
      confirmText="Delete"
      confirmVariant="danger"
      :loading="isDeletingProduct"
      @confirm="confirmProductDelete"
    />

    <category-manager-modal
      v-model="isCategoryModalOpen"
      :categories="adminCategories"
      @create="createCategory"
      @update="updateCategory"
      @delete="deleteCategory"
    />

    <image-preview-modal v-model="isImagePreviewOpen" :url="previewImageUrl" />
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import ProductEditorModal from '../components/shop/modals/ProductEditorModal.vue'
import ShopHero from '../components/shop/ShopHero.vue'
import ShopToolbar from '../components/shop/ShopToolbar.vue'
import ProductGrid from '../components/shop/ProductGrid.vue'
import ProductDetailModal from '../components/shop/modals/ProductDetailModal.vue'
import CategoryManagerModal from '../components/shop/modals/CategoryManagerModal.vue'
import ImagePreviewModal from '../components/shop/modals/ImagePreviewModal.vue'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useShopCatalog } from '../composables/useShopCatalog'
import { useShopProductAdmin } from '../composables/useShopProductAdmin'
import { useShopCategoryAdmin } from '../composables/useShopCategoryAdmin'
import type { ProductResponse } from '@/api/backendAPINinja.schemas.ts'

const { data: profile } = useGetUserProfile()
const isAdmin = computed(() => profile.value?.role === 'admin')

const selectedProduct = ref<ProductResponse | null>(null)

const isDetailOpen = ref(false)
const isProductEditOpen = ref(false)
const isProductDeleteOpen = ref(false)
const isCategoryModalOpen = ref(false)

const isImagePreviewOpen = ref(false)
const previewImageUrl = ref('')

const openProductCreate = () => {
  selectedProduct.value = null
  isProductEditOpen.value = true
}

const openProductEdit = (product: ProductResponse) => {
  selectedProduct.value = product
  isProductEditOpen.value = true
}

const openProductDelete = (product: ProductResponse) => {
  selectedProduct.value = product
  isProductDeleteOpen.value = true
}

const openProductDetail = (product: ProductResponse) => {
  selectedProduct.value = product
  isDetailOpen.value = true
}

const openCategoryModal = () => {
  isCategoryModalOpen.value = true
}

const openImagePreview = (url: string) => {
  if (!url) return
  previewImageUrl.value = url
  isImagePreviewOpen.value = true
}

const {
  currentPage,
  pageSize,
  search,
  selectedCategory,
  selectedType,
  selectedOrdering,
  products,
  totalCount,
  totalPages,
  categoryOptions,
  isLoading,
  isLoadingError,
  error,
} = useShopCatalog()

const {
  avatarFrames,
  isSavingProduct,
  isDeletingProduct,
  submitProductForm,
  confirmProductDelete,
} = useShopProductAdmin()

const { adminCategories, createCategory, updateCategory, deleteCategory } =
  useShopCategoryAdmin(isAdmin)
</script>

<style scoped>
.shop-page {
  display: grid;
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.catalog-section {
  display: grid;
  gap: 0;
}

.shop-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

@media (max-width: 760px) {
  .shop-page {
    padding: 1rem 1rem 2rem;
  }
}
</style>
