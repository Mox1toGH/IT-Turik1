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
      :product="activeProduct"
      :balance="pointsBalance?.balance ?? 0"
      :submitting="isPurchasePending"
      @purchase="handlePurchase"
      @preview="openImagePreview"
    />

    <product-editor-modal
      v-model="isProductFormOpen"
      :mode="editingProduct ? 'edit' : 'create'"
      :product="editingProduct"
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
import ProductEditorModal from '../components/shop/ProductEditorModal.vue'
import ShopHero from '../components/shop/ShopHero.vue'
import ShopToolbar from '../components/shop/ShopToolbar.vue'
import ProductGrid from '../components/shop/ProductGrid.vue'
import ProductDetailModal from '../components/shop/ProductDetailModal.vue'
import CategoryManagerModal from '../components/shop/CategoryManagerModal.vue'
import ImagePreviewModal from '../components/shop/ImagePreviewModal.vue'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useShopCatalog } from '../composables/useShopCatalog'
import { useProductPurchase } from '../composables/useProductPurchase'
import { useShopProductAdmin } from '../composables/useShopProductAdmin'
import { useShopCategoryAdmin } from '../composables/useShopCategoryAdmin'

const { data: profile } = useGetUserProfile()
const isAdmin = computed(() => profile.value?.role === 'admin')

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
  pointsBalance,
  isPurchasePending,
  isDetailOpen,
  activeProduct,
  openProductDetail,
  handlePurchase,
} = useProductPurchase()

const {
  avatarFrames,
  isProductFormOpen,
  editingProduct,
  isProductDeleteOpen,
  isSavingProduct,
  isDeletingProduct,
  openProductCreate,
  openProductEdit,
  openProductDelete,
  submitProductForm,
  confirmProductDelete,
} = useShopProductAdmin()

const {
  adminCategories,
  isCategoryModalOpen,
  openCategoryModal,
  createCategory,
  updateCategory,
  deleteCategory,
} = useShopCategoryAdmin(isAdmin)

const isImagePreviewOpen = ref(false)
const previewImageUrl = ref('')

const openImagePreview = (url: string) => {
  if (!url) return
  previewImageUrl.value = url
  isImagePreviewOpen.value = true
}
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
