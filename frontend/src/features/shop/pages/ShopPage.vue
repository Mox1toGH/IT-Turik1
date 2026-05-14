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
              v-if="product.images[0]?.image || product.avatar_frame?.svg_file || product.digital_asset_url"
              :src="product.images[0]?.image || product.avatar_frame?.svg_file || product.digital_asset_url"
              class="thumb"
              alt="Product image"
              @click="openImagePreview(product.images[0]?.image || product.avatar_frame?.svg_file || product.digital_asset_url || '')"
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
            @click="openImagePreview(image.image)"
          />
        </div>
        <div class="image-row" v-else-if="activeProduct.avatar_frame?.svg_file || activeProduct.digital_asset_url">
          <img
            :src="activeProduct.avatar_frame?.svg_file || activeProduct.digital_asset_url"
            class="detail-image"
            alt="Product image"
            @click="openImagePreview(activeProduct.avatar_frame?.svg_file || activeProduct.digital_asset_url || '')"
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
              :max="Math.max(1, activeProduct.stock_quantity || 0)"
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

    <ui-modal v-model="isCategoryModalOpen" maxWidth="700px">
      <template #title>Categories</template>
      <div class="categories-manager">
        <div class="categories-toolbar">
          <div class="categories-count">Total: {{ adminCategories.length }}</div>
          <input
            v-model.trim="categorySearch"
            class="category-search-input"
            placeholder="Search categories"
          />
        </div>

        <div class="categories-list">
          <article v-if="!filteredCategories.length" class="categories-empty">
            <p>No categories found.</p>
          </article>

          <article
            v-for="category in filteredCategories"
            :key="category.id"
            class="category-item"
            :class="{ editing: editingCategoryId === category.id }"
          >
            <div class="category-main">
              <template v-if="editingCategoryId === category.id">
                <input
                  v-model.trim="categoryForm.name"
                  class="category-inline-input"
                  placeholder="Category name"
                />
              </template>
              <template v-else>
                <p class="category-name">{{ category.name }}</p>
                <span class="category-id">#{{ category.id }}</span>
              </template>
            </div>

            <div class="row-actions">
              <template v-if="editingCategoryId === category.id">
                <button class="action-btn save" @click="submitCategoryForm">Save</button>
                <button class="action-btn cancel" @click="cancelCategoryEdit">Cancel</button>
              </template>
              <template v-else>
                <button class="action-btn edit" @click="startEditCategory(category)">Edit</button>
                <button class="action-btn delete" @click="deleteCategory(category.id)">Delete</button>
              </template>
            </div>
          </article>
        </div>

        <form class="category-create-form" @submit.prevent="submitCategoryForm">
          <label class="category-create-label" for="new-category-name">Create new category</label>
          <div class="category-create-row">
            <input
              id="new-category-name"
              v-model.trim="categoryForm.name"
              class="category-create-input"
              placeholder="Category name"
              required
            />
            <button class="create-btn" type="submit">
              {{ editingCategoryId ? 'Save changes' : 'Add category' }}
            </button>
          </div>
          <p v-if="editingCategoryId" class="edit-hint">
            Editing category #{{ editingCategoryId }}. Click “Cancel” in row to discard.
          </p>
        </form>
      </div>
    </ui-modal>

    <ui-modal v-model="isImagePreviewOpen" maxWidth="min(96vw, 1200px)">
      <template #title>Image Preview</template>
      <div class="image-preview-wrap">
        <img v-if="previewImageUrl" :src="previewImageUrl" class="image-preview-full" alt="Preview" />
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
  useAvatarFrames,
  useShopProducts,
  useShopPurchase,
} from '@/api/queries/shop'
import { useNotification } from '@/composables/useNotification'
import type { ShopCategory, ShopProduct } from '@/api/queries/shop'

const { showNotification } = useNotification()
const { data: profile } = useProfile()
const isAdmin = computed(() => profile.value?.role === 'admin')

const currentPage = ref(1)
const pageSize = ref(12)
const search = ref('')
const selectedCategory = ref('all')
const selectedType = ref<'physical' | 'digital' | 'all'>('all')
const selectedOrdering = ref<'name' | '-name' | 'price' | '-price'>('name')

const { data, isLoading, isLoadingError, error } = useShopProducts(
  computed(() => ({
    page: currentPage.value,
    page_size: pageSize.value,
    search: search.value,
    category: selectedCategory.value === 'all' ? undefined : Number(selectedCategory.value),
    product_type: selectedType.value === 'all' ? undefined : selectedType.value,
    ordering: selectedOrdering.value,
  })),
)
const parsedError = computed(() => parseApiError(error.value))
const products = computed(() => data.value?.results ?? [])
const totalPages = computed(() => Math.max(1, Math.ceil((data.value?.count ?? 0) / pageSize.value)))

const { data: avatarFramesData } = useAvatarFrames()
const avatarFrames = computed(() => avatarFramesData.value?.results ?? [])

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
const isImagePreviewOpen = ref(false)
const previewImageUrl = ref('')
const { data: pointsBalance } = useMyPointsBalance()
const { mutate: purchase, isPending: isPurchasePending } = useShopPurchase()

const openProductDetail = (product: ShopProduct) => {
  activeProduct.value = product
  purchaseQty.value = 1
  purchaseResult.value = ''
  isDetailOpen.value = true
}

const openImagePreview = (url: string) => {
  previewImageUrl.value = url
  isImagePreviewOpen.value = true
}

const handlePurchase = () => {
  if (!activeProduct.value) return
  purchase(
    { data: { product_id: activeProduct.value.id, quantity: Number(purchaseQty.value || 1) } },
    {
      onSuccess: (res: any) => {
        if (res.id) {
          purchaseResult.value = `Success: order #${res.id} created, status ${res.status}.`
        } else {
          purchaseResult.value = res.message || 'Purchase successful.'
        }
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

const { data: adminCategoryData } = useAdminShopCategories({}, { query: { enabled: isAdmin } })
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

const submitProductForm = (body: any) => {
  if (!editingProduct.value) {
    createProduct({ data: body }, {
      onSuccess: () => {
        isProductFormOpen.value = false
        showNotification('Product created.', 'success')
      },
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    })
    return
  }

  updateProduct(
    { id: editingProduct.value.id, data: body },
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
const categoryForm = ref({ name: '' })
const editingCategoryId = ref<number | null>(null)
const categorySearch = ref('')
const filteredCategories = computed(() => {
  const query = categorySearch.value.trim().toLowerCase()
  if (!query) return adminCategories.value
  return adminCategories.value.filter((category) => category.name.toLowerCase().includes(query))
})

const openCategoryCreate = () => {
  isCategoryModalOpen.value = true
  categoryForm.value = { name: '' }
  editingCategoryId.value = null
}

const startEditCategory = (category: ShopCategory) => {
  editingCategoryId.value = category.id
  categoryForm.value = { name: category.name }
}

const cancelCategoryEdit = () => {
  editingCategoryId.value = null
  categoryForm.value = { name: '' }
}

const { mutate: createCategory } = useAdminCreateCategory()
const { mutate: updateCategory } = useAdminUpdateCategory()
const { mutate: removeCategory } = useAdminDeleteCategory()

const submitCategoryForm = () => {
  if (!editingCategoryId.value) {
    createCategory({ data: categoryForm.value }, {
      onSuccess: () => {
        categoryForm.value = { name: '' }
        showNotification('Category created.', 'success')
      },
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    })
    return
  }

  updateCategory(
    { id: editingCategoryId.value, data: categoryForm.value },
    {
      onSuccess: () => {
        editingCategoryId.value = null
        categoryForm.value = { name: '' }
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
  cursor: zoom-in;
}
.image-preview-wrap {
  display: grid;
  place-items: center;
  min-height: min(70vh, 720px);
}
.image-preview-full {
  max-width: 100%;
  max-height: 70vh;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 10px;
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
.categories-manager {
  display: grid;
  gap: 12px;
}
.categories-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.categories-count {
  font-size: 0.85rem;
  color: var(--muted-foreground);
  font-weight: 700;
}
.category-search-input,
.category-inline-input,
.category-create-input {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--background);
  color: var(--foreground);
  padding: 10px 12px;
  font: inherit;
}
.category-search-input {
  max-width: 260px;
}
.categories-list {
  max-height: 320px;
  overflow: auto;
  border: 1px solid color-mix(in srgb, var(--border) 65%, transparent);
  border-radius: 14px;
  padding: 8px;
  display: grid;
  gap: 8px;
}
.categories-empty {
  display: grid;
  place-items: center;
  min-height: 120px;
  color: var(--muted-foreground);
}
.category-item {
  border: 1px solid color-mix(in srgb, var(--border) 65%, transparent);
  border-radius: 12px;
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  background: color-mix(in srgb, var(--muted) 80%, transparent);
}
.category-item.editing {
  border-color: color-mix(in srgb, var(--primary) 60%, var(--border));
  background: color-mix(in srgb, var(--primary) 7%, transparent);
}
.category-main {
  min-width: 0;
  display: grid;
  gap: 3px;
}
.category-name {
  margin: 0;
  font-weight: 700;
  overflow-wrap: anywhere;
}
.category-id {
  color: var(--muted-foreground);
  font-size: 0.8rem;
}
.action-btn {
  border: 1px solid transparent;
  border-radius: 9px;
  padding: 6px 10px;
  background: transparent;
  cursor: pointer;
  font-weight: 700;
}
.action-btn.edit {
  color: #00998a;
  border-color: color-mix(in srgb, #00998a 55%, transparent);
}
.action-btn.delete {
  color: var(--destructive);
  border-color: color-mix(in srgb, var(--destructive) 55%, transparent);
}
.action-btn.save {
  color: var(--primary);
  border-color: color-mix(in srgb, var(--primary) 55%, transparent);
}
.action-btn.cancel {
  color: var(--muted-foreground);
  border-color: color-mix(in srgb, var(--muted-foreground) 40%, transparent);
}
.category-create-form {
  display: grid;
  gap: 8px;
}
.category-create-label {
  font-size: 0.84rem;
  color: var(--muted-foreground);
  font-weight: 700;
}
.category-create-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}
.create-btn {
  border: none;
  border-radius: 10px;
  padding: 0 16px;
  background: var(--primary);
  color: var(--primary-foreground);
  font-weight: 800;
  cursor: pointer;
}
.edit-hint {
  margin: 0;
  font-size: 0.8rem;
  color: var(--muted-foreground);
}

@media (max-width: 900px) {
  .toolbar {
    grid-template-columns: 1fr;
  }
  .head {
    flex-direction: column;
    align-items: flex-start;
  }
  .categories-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .category-search-input {
    max-width: none;
  }
  .category-item {
    flex-direction: column;
    align-items: stretch;
  }
  .row-actions {
    justify-content: flex-end;
  }
  .category-create-row {
    grid-template-columns: 1fr;
  }
}
</style>
