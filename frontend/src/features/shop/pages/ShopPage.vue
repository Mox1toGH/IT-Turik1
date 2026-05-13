<template>
  <section class="page-shell shop-page">
    <ui-card>
      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">Shop</p>
            <h1 class="section-title">Catalog</h1>
          </div>
          <div class="head-actions">
            <ui-button v-if="isAdmin" variant="secondary" @click="openCategoryCreate"
              >Manage Categories</ui-button
            >
            <ui-button v-if="isAdmin" @click="openProductCreate">Create Product</ui-button>
            <ui-button v-if="isAdmin" variant="secondary" as-link to="/admin/shop-orders"
              >Admin Orders</ui-button
            >
          </div>
        </div>
      </template>

      <div class="toolbar">
        <ui-input v-model="search" placeholder="Search by name" />
        <ui-select v-model="selectedCategory" :options="categoryOptions" />
        <ui-select v-model="selectedType" :options="typeOptions" />
        <ui-select v-model="selectedOrdering" :options="orderingOptions" />
      </div>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div class="grid">
            <ui-card v-for="i in 6" :key="i"
              ><ui-skeleton variant="rect" width="100%" height="120px"
            /></ui-card>
          </div>
        </template>

        <p v-if="isLoadingError" class="text-muted">
          Failed to load products ({{ parsedError?.message || parsedError?.code }})
        </p>
        <p v-else-if="!products.length" class="text-muted">No products found.</p>

        <div v-else class="grid">
          <ui-card
            v-for="product in products"
            :key="product.id"
            class="product-card"
            :class="{ unavailable: !product.is_available }"
          >
            <template #header>
              <div class="card-head">
                <strong>{{ product.name }}</strong>
                <ui-badge :variant="product.is_available ? 'green' : 'gray'">{{
                  product.is_available ? 'Available' : 'Out of stock'
                }}</ui-badge>
              </div>
            </template>

            <img
              v-if="product.images[0]?.image"
              :src="product.images[0].image"
              class="thumb"
              alt="Product image"
            />
            <p class="price">{{ product.price }} pts</p>
            <p class="meta">{{ product.category.name }} | {{ product.product_type }}</p>
            <p class="desc">{{ product.description || 'No description' }}</p>

            <div class="card-actions">
              <ui-button size="sm" variant="secondary" @click="openProductDetail(product)"
                >View</ui-button
              >
              <ui-button v-if="isAdmin" size="sm" @click="openProductEdit(product)">Edit</ui-button>
              <ui-button
                v-if="isAdmin"
                size="sm"
                variant="danger"
                @click="openProductDelete(product)"
                >Delete</ui-button
              >
            </div>
          </ui-card>
        </div>
      </ui-skeleton-loader>

      <div v-if="totalPages > 1" class="pagination">
        <ui-button variant="secondary" :disabled="currentPage === 1" @click="currentPage -= 1"
          >Prev</ui-button
        >
        <span>Page {{ currentPage }} / {{ totalPages }}</span>
        <ui-button
          variant="secondary"
          :disabled="currentPage === totalPages"
          @click="currentPage += 1"
          >Next</ui-button
        >
      </div>
    </ui-card>

    <ui-modal v-model="isDetailOpen" maxWidth="760px">
      <template #title>{{ activeProduct?.name }}</template>
      <div v-if="activeProduct" class="detail-body">
        <div class="image-row" v-if="activeProduct.images.length">
          <img
            v-for="image in activeProduct.images"
            :key="image.id"
            :src="image.image"
            class="detail-image"
            alt="Product image"
          />
        </div>
        <p>{{ activeProduct.description || 'No description' }}</p>
        <p><strong>Price:</strong> {{ activeProduct.price }} points</p>
        <p><strong>Stock:</strong> {{ activeProduct.stock_quantity }}</p>

        <div class="purchase-box">
          <p><strong>Current balance:</strong> {{ pointsBalance?.balance ?? 0 }}</p>
          <label>
            Quantity
            <ui-input
              v-model="purchaseQty"
              type="number"
              :min="1"
              :max="Math.max(1, activeProduct.stock_quantity)"
            />
          </label>
          <p><strong>Will deduct:</strong> {{ (purchaseQty || 1) * activeProduct.price }} points</p>
          <ui-button
            :disabled="isPurchasePending || !activeProduct.is_available"
            @click="handlePurchase"
            >Buy</ui-button
          >
          <p v-if="purchaseResult" class="purchase-result">{{ purchaseResult }}</p>
        </div>
      </div>
    </ui-modal>

    <product-editor-modal
      v-model="isProductFormOpen"
      :mode="editingProduct ? 'edit' : 'create'"
      :product="editingProduct"
      :categories="adminCategories"
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

    <ui-modal v-model="isCategoryModalOpen" maxWidth="700px">
      <template #title>Categories</template>
      <div class="category-list">
        <ui-card v-for="category in adminCategories" :key="category.id" class="category-row">
          <div>
            <strong>{{ category.name }}</strong>
            <p class="text-muted">{{ category.description || '-' }}</p>
          </div>
          <div class="row-actions">
            <ui-button size="sm" @click="startEditCategory(category)">Edit</ui-button>
            <ui-button size="sm" variant="danger" @click="deleteCategory(category.id)"
              >Delete</ui-button
            >
          </div>
        </ui-card>

        <form class="modal-form" @submit.prevent="submitCategoryForm">
          <ui-input v-model="categoryForm.name" placeholder="Category name" required />
          <ui-input v-model="categoryForm.description" placeholder="Description" />
          <ui-button type="submit">{{
            editingCategoryId ? 'Save category' : 'Add category'
          }}</ui-button>
        </form>
      </div>
    </ui-modal>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import ProductEditorModal from '@/features/shop/components/admin/ProductEditorModal.vue'
import { parseApiError } from '@/api/errors'
import { useProfile } from '@/api/queries/accounts'
import { useMyPointsBalance } from '@/api/queries/points'
import {
  useAdminCreateCategory,
  useAdminCreateProduct,
  useAdminDeleteCategory,
  useAdminDeleteProduct,
  useAdminShopCategories,
  useAdminUpdateCategory,
  useAdminUpdateProduct,
  useShopProducts,
  useShopPurchase,
} from '@/api/queries/shop'
import { useNotification } from '@/composables/useNotification'
import type { ShopCategory, ShopProduct, UpsertProductBody } from '@/api/services/shop/types'

const { showNotification } = useNotification()
const { data: profile } = useProfile()
const isAdmin = computed(() => profile.value?.role === 'admin')

const currentPage = ref(1)
const pageSize = ref(12)
const search = ref('')
const selectedCategory = ref('all')
const selectedType = ref<'physical' | 'digital' | 'all'>('all')
const selectedOrdering = ref<'name' | '-name' | 'price' | '-price'>('name')

const { data, isLoading, isLoadingError, error } = useShopProducts({
  page: currentPage,
  pageSize,
  search,
  category: computed(() =>
    selectedCategory.value === 'all' ? null : Number(selectedCategory.value),
  ),
  productType: selectedType,
  ordering: selectedOrdering,
})
const parsedError = computed(() => parseApiError(error.value))
const products = computed(() => data.value?.results ?? [])
const totalPages = computed(() => Math.max(1, Math.ceil((data.value?.count ?? 0) / pageSize.value)))

watch([search, selectedCategory, selectedType, selectedOrdering], () => {
  currentPage.value = 1
})

const categoryOptions = computed(() => {
  const set = new Map<number, string>()
  for (const item of products.value) set.set(item.category.id, item.category.name)
  return [
    { value: 'all', label: 'All categories' },
    ...Array.from(set.entries()).map(([id, name]) => ({ value: String(id), label: name })),
  ]
})

const typeOptions = [
  { value: 'all', label: 'All types' },
  { value: 'physical', label: 'Physical' },
  { value: 'digital', label: 'Digital' },
]

const orderingOptions = [
  { value: 'name', label: 'Name A-Z' },
  { value: '-name', label: 'Name Z-A' },
  { value: 'price', label: 'Price low-high' },
  { value: '-price', label: 'Price high-low' },
]

const isDetailOpen = ref(false)
const activeProduct = ref<ShopProduct | null>(null)
const purchaseQty = ref(1)
const purchaseResult = ref('')
const { data: pointsBalance } = useMyPointsBalance()
const { mutate: purchase, isPending: isPurchasePending } = useShopPurchase()

const openProductDetail = (product: ShopProduct) => {
  activeProduct.value = product
  purchaseQty.value = 1
  purchaseResult.value = ''
  isDetailOpen.value = true
}

const handlePurchase = () => {
  if (!activeProduct.value) return
  purchase(
    { productId: activeProduct.value.id, quantity: Number(purchaseQty.value || 1) },
    {
      onSuccess: (order) => {
        purchaseResult.value = `Success: order #${order.id} created, status ${order.status}.`
        showNotification('Purchase successful.', 'success')
      },
      onError: (e) => {
        const parsed = parseApiError(e)
        purchaseResult.value = parsed?.message || 'Purchase failed.'
        showNotification(parsed?.message, 'error')
      },
    },
  )
}

const { data: adminCategoryData } = useAdminShopCategories({}, { enabled: isAdmin })
const adminCategories = computed(() => adminCategoryData.value?.results ?? [])
const isProductFormOpen = ref(false)
const editingProduct = ref<ShopProduct | null>(null)
const isProductDeleteOpen = ref(false)
const deletingProduct = ref<ShopProduct | null>(null)

const openProductCreate = () => {
  editingProduct.value = null
  isProductFormOpen.value = true
}

const openProductEdit = (product: ShopProduct) => {
  editingProduct.value = product
  isProductFormOpen.value = true
}

const openProductDelete = (product: ShopProduct) => {
  deletingProduct.value = product
  isProductDeleteOpen.value = true
}

const { mutate: createProduct, isPending: isCreatingProduct } = useAdminCreateProduct()
const { mutate: updateProduct, isPending: isUpdatingProduct } = useAdminUpdateProduct()
const { mutate: deleteProduct, isPending: isDeletingProduct } = useAdminDeleteProduct()
const isSavingProduct = computed(() => isCreatingProduct.value || isUpdatingProduct.value)

const submitProductForm = (body: UpsertProductBody) => {
  if (!editingProduct.value) {
    createProduct(body, {
      onSuccess: () => {
        isProductFormOpen.value = false
        showNotification('Product created.', 'success')
      },
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    })
    return
  }

  updateProduct(
    { id: editingProduct.value.id, body },
    {
      onSuccess: () => {
        isProductFormOpen.value = false
        showNotification('Product updated.', 'success')
      },
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    },
  )
}

const confirmProductDelete = () => {
  if (!deletingProduct.value) return
  deleteProduct(
    { id: deletingProduct.value.id },
    {
      onSuccess: () => {
        isProductDeleteOpen.value = false
        deletingProduct.value = null
        showNotification('Product deleted.', 'success')
      },
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    },
  )
}

const isCategoryModalOpen = ref(false)
const categoryForm = ref({ name: '', description: '' })
const editingCategoryId = ref<number | null>(null)

const openCategoryCreate = () => {
  isCategoryModalOpen.value = true
  categoryForm.value = { name: '', description: '' }
  editingCategoryId.value = null
}

const startEditCategory = (category: ShopCategory) => {
  editingCategoryId.value = category.id
  categoryForm.value = { name: category.name, description: category.description }
}

const { mutate: createCategory } = useAdminCreateCategory()
const { mutate: updateCategory } = useAdminUpdateCategory()
const { mutate: removeCategory } = useAdminDeleteCategory()

const submitCategoryForm = () => {
  if (!editingCategoryId.value) {
    createCategory(categoryForm.value, {
      onSuccess: () => {
        categoryForm.value = { name: '', description: '' }
        showNotification('Category created.', 'success')
      },
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    })
    return
  }

  updateCategory(
    { id: editingCategoryId.value, body: categoryForm.value },
    {
      onSuccess: () => {
        editingCategoryId.value = null
        categoryForm.value = { name: '', description: '' }
        showNotification('Category updated.', 'success')
      },
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    },
  )
}

const deleteCategory = (id: number) => {
  removeCategory(
    { id },
    {
      onSuccess: () => showNotification('Category deleted.', 'success'),
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    },
  )
}
</script>

<style scoped>
.shop-page {
  display: grid;
  gap: 1rem;
}
.head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}
.head-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.toolbar {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 12px;
}
.grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
}
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
.thumb {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 8px;
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
}
.card-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.pagination {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}
.detail-body {
  display: grid;
  gap: 10px;
}
.image-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
}
.detail-image {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
}
.purchase-box {
  display: grid;
  gap: 8px;
  border: 1px solid var(--border);
  padding: 10px;
  border-radius: 10px;
}
.purchase-result {
  font-weight: 600;
}
.modal-form {
  display: grid;
  gap: 8px;
}
.category-list {
  display: grid;
  gap: 10px;
}
.category-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.row-actions {
  display: flex;
  gap: 6px;
}

@media (max-width: 900px) {
  .toolbar {
    grid-template-columns: 1fr;
  }
  .head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
