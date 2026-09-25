<template>
  <ui-modal
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    maxWidth="980px"
    scrollable
  >
    <template #title>
      <div class="modal-title">
        <p class="section-eyebrow">Shop workspace</p>
        <h2>{{ mode === 'edit' ? 'Edit product' : 'Create product' }}</h2>
      </div>
    </template>

    <form class="editor" @submit.prevent="handleSubmit">
      <div class="editor-form">
        <ui-card variant="form" class="form-panel">
          <div class="panel-header">
            <span class="step-marker">01</span>
            <div>
              <h3>Basics</h3>
              <p class="text-muted">Name the product and describe what it is.</p>
            </div>
          </div>

          <label class="field">
            <span class="label">Name</span>
            <ui-input v-model.trim="form.name" placeholder="e.g. Mechanical Keyboard" />
            <small v-if="errors.name" class="error">{{ errors.name }}</small>
          </label>

          <label class="field">
            <span class="label">Description</span>
            <ui-text-area
              v-model.trim="form.description"
              rows="4"
              placeholder="Short product description"
            />
          </label>
        </ui-card>

        <ui-card variant="form" class="form-panel">
          <div class="panel-header">
            <span class="step-marker">02</span>
            <div>
              <h3>Pricing &amp; stock</h3>
              <p class="text-muted">Set what it costs and how many are available.</p>
            </div>
          </div>

          <div class="row two">
            <label class="field">
              <span class="label">Price (points)</span>
              <ui-number-input v-model.number="form.price" min="0" />
              <small v-if="errors.price" class="error">{{ errors.price }}</small>
            </label>

            <label class="field">
              <span class="label">Stock quantity</span>
              <ui-number-input v-model.number="form.stock_quantity" min="0" />
              <small v-if="errors.stock_quantity" class="error">{{ errors.stock_quantity }}</small>
            </label>
          </div>

          <div class="row two">
            <label class="field">
              <span class="label">Category</span>
              <ui-select
                v-model="form.category_id"
                :options="categoryOptions"
                placeholder="Select a category"
              />
              <small v-if="errors.category_id" class="error">{{ errors.category_id }}</small>
            </label>

            <label class="field">
              <span class="label">Product type</span>
              <ui-select
                v-model="form.product_type!"
                :options="productTypeOptions"
                placeholder="Select a type"
              />
            </label>
          </div>
        </ui-card>

        <ui-card v-if="form.product_type === 'digital'" variant="form" class="form-panel">
          <div class="panel-header">
            <span class="step-marker">03</span>
            <div>
              <h3>Digital asset</h3>
              <p class="text-muted">Attach the avatar frame this product unlocks.</p>
            </div>
          </div>

          <div class="row three">
            <label v-if="mode === 'edit'" class="field">
              <span class="label">Avatar frame (existing)</span>
              <ui-select
                v-model="avatarFrameModel"
                :options="avatarFrameOptions"
                placeholder="Not selected"
              />
              <small v-if="errors.avatar_frame_id" class="error">{{
                errors.avatar_frame_id
              }}</small>
            </label>

            <label class="field frame-upload-field">
              <span class="label">{{
                mode === 'create' ? 'Upload frame file (.svg)' : 'Or upload a new one (.svg)'
              }}</span>
              <ui-file-drop
                v-model="selectedFrameFile"
                accept=".svg"
                :multiple="false"
                hint="SVG only"
              />
            </label>
          </div>
        </ui-card>

        <ui-card variant="form" class="form-panel">
          <div class="panel-header">
            <span class="step-marker">{{ form.product_type === 'digital' ? '04' : '03' }}</span>
            <div>
              <h3>Media &amp; visibility</h3>
              <p class="text-muted">Add photos and control whether it shows in the catalog.</p>
            </div>
          </div>

          <label class="switcher">
            <ui-switch v-model="form.is_active" />
            <span>Active in catalog</span>
          </label>

          <label class="upload-block">
            <span class="label">Images (multiple allowed)</span>
            <ui-file-drop v-model="selectedFiles" accept="image/*" multiple />
            <span class="upload-note">PNG, JPG, WEBP. The first file will be used as cover.</span>
          </label>

          <div v-if="newPreviews.length" class="preview-grid">
            <article v-for="(url, i) in newPreviews" :key="url" class="preview-tile">
              <img :src="url" alt="New image" @click="openImagePreview(url)" />
              <ui-button size="sm" variant="danger" class="remove-btn" @click="removePicked(i)"
                >Remove</ui-button
              >
            </article>
          </div>
        </ui-card>
      </div>

      <aside class="summary-panel" aria-label="Product summary">
        <ui-card variant="stat" class="summary-stat">
          <strong>{{ form.price || 0 }}</strong>
          <span>Points</span>
        </ui-card>

        <ui-card variant="form" class="summary-card">
          <p class="section-eyebrow">Live preview</p>

          <article class="mock-card" :class="{ inactive: !form.is_active || !isAvailable }">
            <img
              v-if="cover"
              :src="cover"
              alt="cover"
              class="cover"
              @click="openImagePreview(cover)"
            />
            <div v-else class="cover cover-empty">No image</div>
            <div class="mock-content">
              <strong class="mock-name" :title="form.name">{{
                truncateText(form.name, 100) || 'Product name'
              }}</strong>
              <p class="mock-meta">{{ selectedCategoryName }} | {{ form.product_type }}</p>
              <p class="mock-price">{{ form.price || 0 }} pts</p>
              <p class="mock-desc" :title="form.description">
                {{ truncateText(form.description || 'Product description will appear here.', 150) }}
              </p>
            </div>
          </article>

          <div class="summary-list">
            <ui-card variant="inset" class="summary-list-item">
              <span>Stock</span>
              <strong>{{ form.stock_quantity || 0 }}</strong>
            </ui-card>
            <ui-card variant="inset" class="summary-list-item">
              <span>Status</span>
              <strong>{{ form.is_active ? 'Active' : 'Inactive' }}</strong>
            </ui-card>
            <ui-card variant="inset" class="summary-list-item">
              <span>Availability</span>
              <strong>{{ isAvailable ? 'Available' : 'Out of stock' }}</strong>
            </ui-card>
          </div>
        </ui-card>
      </aside>
    </form>

    <template #footer>
      <div class="footer-actions">
        <ui-button
          variant="secondary"
          :disabled="submitting"
          @click="emit('update:modelValue', false)"
          >Cancel</ui-button
        >
        <ui-button :disabled="submitting" @click="handleSubmit">{{
          submitting ? 'Saving...' : mode === 'edit' ? 'Save changes' : 'Create product'
        }}</ui-button>
      </div>
    </template>
  </ui-modal>

  <ui-modal
    :model-value="isImagePreviewOpen"
    @update:model-value="isImagePreviewOpen = $event"
    maxWidth="min(96vw, 1200px)"
  >
    <template #title>Image Preview</template>
    <div class="image-preview-wrap">
      <img v-if="previewImageUrl" :src="previewImageUrl" class="image-preview-full" alt="Preview" />
    </div>
  </ui-modal>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiFileDrop from '@/components/ui/UiFileDrop.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import type { ShopCategory } from '@/api/services/shop/types'
import type { CreateAdminProductMutationBody } from '@/api/shop/shop'
import UiInput from '@/components/ui/UiInput.vue'
import UiNumberInput from '@/components/ui/UiNumberInput.vue'
import UiTextArea from '@/components/ui/UiTextArea.vue'
import UiSwitch from '@/components/ui/UiSwitch.vue'
import { truncateText } from '@/lib/utils'
import {
  CreateAdminProductBodyProductType,
  type AvatarFrameResponse,
  type ProductResponse,
} from '@/api/backendAPINinja.schemas'

interface Props {
  modelValue: boolean
  mode: 'create' | 'edit'
  product?: ProductResponse | null
  categories: ShopCategory[]
  avatarFrames: AvatarFrameResponse[]
  submitting?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  product: null,
  submitting: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'submit', value: CreateAdminProductMutationBody): void
}>()

const selectedFiles = ref<File[]>([])
const pickedFiles = ref<File[]>([])
const newPreviews = ref<string[]>([])
const selectedFrameFile = ref<File[]>([])
const isImagePreviewOpen = ref(false)
const previewImageUrl = ref('')

const form = ref<CreateAdminProductMutationBody>({
  name: '',
  description: '',
  price: 0,
  stock_quantity: 0,
  category_id: 0,
  product_type: CreateAdminProductBodyProductType.physical,
  avatar_frame_id: undefined,
  avatar_frame_file: undefined,
  digital_asset_url: '',
  is_active: true,
  uploaded_images: [],
})

const errors = ref<Record<string, string>>({})

// UiSelect options -----------------------------------------------------

const categoryOptions = computed(() =>
  props.categories.map((category) => ({ value: category.id, label: category.name })),
)

const productTypeOptions = [
  { value: 'physical', label: 'Physical' },
  { value: 'digital', label: 'Digital' },
]

const NO_FRAME = 0

const avatarFrameOptions = computed(() => [
  { value: NO_FRAME, label: 'Not selected' },
  ...props.avatarFrames.map((frame) => ({ value: frame.id, label: frame.name })),
])

// UiSelect can't represent `undefined`, so proxy it through a sentinel value.
const avatarFrameModel = computed({
  get: () => form.value.avatar_frame_id ?? NO_FRAME,
  set: (val) => {
    const numeric = Number(val)
    form.value.avatar_frame_id = numeric === NO_FRAME ? undefined : numeric
  },
})

// ------------------------------------------------------------------------

const resetForm = () => {
  const p = props.product
  form.value = {
    name: p?.name || '',
    description: p?.description || '',
    price: p?.price || 0,
    stock_quantity: p?.stock_quantity || 0,
    category_id: p?.category?.id || props.categories[0]?.id || 0,
    product_type:
      p?.product_type === CreateAdminProductBodyProductType.digital
        ? CreateAdminProductBodyProductType.digital
        : CreateAdminProductBodyProductType.physical,
    avatar_frame_id: p?.avatar_frame?.id,
    avatar_frame_file: undefined,
    digital_asset_url: p?.digital_asset_url || '', // kept for backward compatibility
    is_active: p?.is_active ?? true,
    uploaded_images: [],
  }
  errors.value = {}
  clearPicked()
  selectedFrameFile.value = []
}

const clearPicked = () => {
  for (const url of newPreviews.value) URL.revokeObjectURL(url)
  newPreviews.value = []
  pickedFiles.value = []
  if (selectedFiles.value.length) selectedFiles.value = []
}

watch(
  () => [props.modelValue, props.product, props.categories.length],
  ([open]) => {
    if (open) resetForm()
  },
  { deep: true },
)

watch(selectedFiles, (files) => {
  for (const url of newPreviews.value) URL.revokeObjectURL(url)
  pickedFiles.value = [...files]
  newPreviews.value = files.map((file) => URL.createObjectURL(file))
})

watch(selectedFrameFile, (files) => {
  form.value.avatar_frame_file = files[0] ?? undefined
})

const removePicked = (index: number) => {
  const removed = newPreviews.value.splice(index, 1)
  if (removed[0]) URL.revokeObjectURL(removed[0])
  pickedFiles.value.splice(index, 1)
  selectedFiles.value = [...pickedFiles.value]
}

const openImagePreview = (url: string) => {
  previewImageUrl.value = url
  isImagePreviewOpen.value = true
}

const selectedCategoryName = computed(() => {
  return props.categories.find((c) => c.id === Number(form.value.category_id))?.name || 'Category'
})

const existingCover = computed(
  () => props.product?.images?.[0]?.image || props.product?.digital_asset_url || '',
)
const cover = computed(() => newPreviews.value[0] || existingCover.value)
const isAvailable = computed(() => Number(form.value.stock_quantity || 0) > 0)

const validate = () => {
  const next: Record<string, string> = {}
  if (!form.value.name.trim()) next.name = 'Please enter a product name.'
  if (Number(form.value.price) < 0) next.price = 'Price cannot be negative.'
  if (Number(form.value.stock_quantity) < 0) next.stock_quantity = 'Stock cannot be negative.'
  if (!Number(form.value.category_id)) next.category_id = 'Please select a category.'
  if (
    form.value.product_type === 'digital' &&
    !form.value.avatar_frame_id &&
    !form.value.avatar_frame_file &&
    !form.value.digital_asset_url?.trim() &&
    pickedFiles.value.length === 0
  ) {
    next.avatar_frame_id =
      'Select an avatar frame, provide a digital asset URL, or upload an image.'
  }
  errors.value = next
  return Object.keys(next).length === 0
}

const handleSubmit = () => {
  if (!validate()) return
  const payload: CreateAdminProductMutationBody = {
    ...form.value,
  }

  if (form.value.avatar_frame_file) {
    payload.avatar_frame_file = form.value.avatar_frame_file
  } else {
    delete payload.avatar_frame_file
  }

  if (pickedFiles.value.length > 0) {
    payload.uploaded_images = [...pickedFiles.value]
  } else {
    delete payload.uploaded_images
  }

  emit('submit', payload)
}
</script>

<style scoped>
.modal-title h2 {
  margin: 0.2rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.editor {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(240px, 0.42fr);
  gap: 14px;
  align-items: start;
}

.editor-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
}

.form-panel.card {
  display: grid;
  gap: 12px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
}

.panel-header h3 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-lg, 1.1rem);
  font-weight: 800;
}

.panel-header p {
  margin: 0.2rem 0 0;
}

.field {
  display: grid;
  gap: 6px;
  margin-bottom: 4px;
}

.label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--muted-foreground);
}

.row.two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.row.three {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.frame-upload-field {
  align-content: start;
}

.switcher {
  margin: 0 0 6px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.upload-block {
  display: grid;
  gap: 6px;
}

.upload-note {
  font-size: 0.8rem;
  color: var(--muted-foreground);
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  gap: 8px;
}

.preview-tile {
  position: relative;
}

.preview-tile img {
  width: 100%;
  height: 86px;
  border-radius: 9px;
  object-fit: cover;
  cursor: zoom-in;
}

.remove-btn {
  margin-top: 4px;
  width: 100%;
}

.summary-panel {
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
}

.summary-stat {
  justify-content: flex-start;
}

.summary-stat strong {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  line-height: var(--text-2xl--line-height);
  font-weight: 800;
}

.summary-stat span {
  color: var(--muted-foreground);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.summary-card.card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mock-card {
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  background: var(--card);
}

.mock-card.inactive {
  opacity: 0.7;
  filter: grayscale(1);
}

.cover {
  width: 100%;
  height: 150px;
  object-fit: cover;
  display: block;
  cursor: zoom-in;
}

.cover-empty {
  display: grid;
  place-items: center;
  color: var(--muted-foreground);
  background: color-mix(in srgb, var(--muted) 90%, transparent);
}

.mock-name {
  word-break: break-word;
}

.mock-content {
  padding: 10px;
  display: grid;
  gap: 5px;
}

.mock-meta {
  margin: 0;
  font-size: 0.82rem;
  color: var(--muted-foreground);
}

.mock-price {
  margin: 0;
  font-weight: 800;
}

.mock-desc {
  margin: 0;
  font-size: 0.9rem;
  word-break: break-word;
}

.summary-list {
  display: grid;
  gap: 0.6rem;
}

.summary-list-item.card {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}

.summary-list span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
}

.summary-list strong {
  text-align: right;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

.error {
  color: var(--destructive);
  font-size: 0.8rem;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
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

@media (max-width: 920px) {
  .editor {
    grid-template-columns: 1fr;
  }

  .summary-panel {
    position: static;
  }

  .row.two {
    grid-template-columns: 1fr;
  }
}
</style>
