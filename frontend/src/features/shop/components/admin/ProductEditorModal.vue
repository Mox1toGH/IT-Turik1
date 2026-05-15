<template>
  <ui-modal
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    maxWidth="980px"
    scrollable
  >
    <template #title>
      <h2>
        {{ mode === 'edit' ? 'Редагування товару' : 'Створення товару' }}
      </h2>
    </template>

    <form class="editor" @submit.prevent="handleSubmit">
      <section class="panel form-panel">
        <label class="field">
          <span class="label">Назва</span>
          <ui-input v-model.trim="form.name" placeholder="Напр. Mechanical Keyboard" />
          <small v-if="errors.name" class="error">{{ errors.name }}</small>
        </label>

        <label class="field">
          <span class="label">Опис</span>
          <ui-text-area
            v-model.trim="form.description"
            rows="4"
            placeholder="Короткий опис товару"
          />
        </label>

        <div class="row two">
          <label class="field">
            <span class="label">Ціна (points)</span>
            <ui-input v-model.number="form.price" type="number" min="0" />
            <small v-if="errors.price" class="error">{{ errors.price }}</small>
          </label>

          <label class="field">
            <span class="label">Кількість на складі</span>
            <ui-input type="number" v-model.number="form.stock_quantity" min="0" />
            <small v-if="errors.stock_quantity" class="error">{{ errors.stock_quantity }}</small>
          </label>
        </div>

        <div class="row two">
          <label class="field">
            <span class="label">Категорія</span>
            <select v-model.number="form.category_id" class="native-select">
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
            <small v-if="errors.category_id" class="error">{{ errors.category_id }}</small>
          </label>

          <label class="field">
            <span class="label">Тип товару</span>
            <select v-model="form.product_type" class="native-select">
              <option value="physical">Physical</option>
              <option value="digital">Digital</option>
            </select>
          </label>
        </div>

        <div v-if="form.product_type === 'digital'" class="row" :class="{ two: mode === 'edit' }">
          <label v-if="mode === 'edit'" class="field">
            <span class="label">Рамка аватара (існуюча)</span>
            <select v-model.number="form.avatar_frame_id" class="native-select">
              <option :value="undefined">Не вибрано</option>
              <option v-for="frame in avatarFrames" :key="frame.id" :value="frame.id">
                {{ frame.name }}
              </option>
            </select>
            <small v-if="errors.avatar_frame_id" class="error">{{ errors.avatar_frame_id }}</small>
          </label>

          <label class="field">
            <span class="label">{{
              mode === 'create' ? 'Завантажити файл рамки (.svg)' : 'Або завантажити нову (.svg)'
            }}</span>
            <input class="native-file" type="file" accept=".svg" @change="onPickFrameFile" />
            <small v-if="frameFileName" class="file-name">{{ frameFileName }}</small>
          </label>
        </div>

        <label class="switcher">
          <ui-switch v-model="form.is_active" />
          <span>Активний у каталозі</span>
        </label>

        <label class="upload-block">
          <span class="label">Зображення (можна декілька)</span>
          <input
            ref="fileInput"
            class="native-file"
            type="file"
            accept="image/*"
            multiple
            @change="onPickFiles"
          />
          <span class="upload-note">PNG, JPG, WEBP. Перший файл буде обкладинкою.</span>
        </label>

        <div v-if="newPreviews.length" class="preview-grid">
          <article v-for="(url, i) in newPreviews" :key="url" class="preview-tile">
            <img :src="url" alt="Нове зображення" @click="openImagePreview(url)" />
            <ui-button size="sm" variant="danger" class="remove-btn" @click="removePicked(i)"
              >Remove</ui-button
            >
          </article>
        </div>
      </section>

      <section class="panel preview-panel">
        <p class="preview-title">Live Preview</p>
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
              {{ truncateText(form.description || 'Опис товару з’явиться тут.', 150) }}
            </p>
          </div>
        </article>

        <div class="summary">
          <p><strong>Склад:</strong> {{ form.stock_quantity || 0 }}</p>
          <p><strong>Статус:</strong> {{ form.is_active ? 'Active' : 'Inactive' }}</p>
          <p>
            <strong>Доступність:</strong>
            {{ isAvailable ? 'Available' : 'Out of stock' }}
          </p>
        </div>
      </section>
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
import type { ShopCategory } from '@/api/services/shop/types'
import type { AvatarFrame, Product } from '@/api/.ts.schemas'
import type { CreateAdminProductMutationBody } from '@/api/shop/shop'
import UiInput from '@/components/ui/UiInput.vue'
import UiTextArea from '@/components/ui/UiTextArea.vue'
import UiSwitch from '@/components/ui/UiSwitch.vue'
import { truncateText } from '@/lib/utils'

interface Props {
  modelValue: boolean
  mode: 'create' | 'edit'
  product?: Product | null
  categories: ShopCategory[]
  avatarFrames: AvatarFrame[]
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

const fileInput = ref<HTMLInputElement | null>(null)
const pickedFiles = ref<File[]>([])
const newPreviews = ref<string[]>([])
const isImagePreviewOpen = ref(false)
const previewImageUrl = ref('')

const form = ref<CreateAdminProductMutationBody>({
  name: '',
  description: '',
  price: 0,
  stock_quantity: 0,
  category_id: 0,
  product_type: 'physical',
  avatar_frame_id: undefined,
  avatar_frame_file: undefined,
  digital_asset_url: '',
  is_active: true,
  uploaded_images: [],
})

const frameFileName = ref('')

const errors = ref<Record<string, string>>({})

const resetForm = () => {
  const p = props.product
  form.value = {
    name: p?.name || '',
    description: p?.description || '',
    price: p?.price || 0,
    stock_quantity: p?.stock_quantity || 0,
    category_id: p?.category?.id || props.categories[0]?.id || 0,
    product_type: p?.product_type || 'physical',
    avatar_frame_id: p?.avatar_frame?.id,
    avatar_frame_file: undefined,
    digital_asset_url: p?.digital_asset_url || '', // kept for backward compatibility
    is_active: p?.is_active ?? true,
    uploaded_images: [],
  }
  frameFileName.value = ''
  errors.value = {}
  clearPicked()
}

const clearPicked = () => {
  for (const url of newPreviews.value) URL.revokeObjectURL(url)
  newPreviews.value = []
  pickedFiles.value = []
  if (fileInput.value) fileInput.value.value = ''
}

watch(
  () => [props.modelValue, props.product, props.categories.length],
  ([open]) => {
    if (open) resetForm()
  },
  { deep: true },
)

const onPickFiles = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files || [])
  clearPicked()
  pickedFiles.value = files
  newPreviews.value = files.map((file) => URL.createObjectURL(file))
}

const removePicked = (index: number) => {
  const removed = newPreviews.value.splice(index, 1)
  if (removed[0]) URL.revokeObjectURL(removed[0])
  pickedFiles.value.splice(index, 1)
}

const onPickFrameFile = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    form.value.avatar_frame_file = file
    frameFileName.value = file.name
  } else {
    form.value.avatar_frame_file = undefined
    frameFileName.value = ''
  }
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
  if (!form.value.name.trim()) next.name = 'Вкажіть назву товару.'
  if (Number(form.value.price) < 0) next.price = 'Ціна не може бути від’ємною.'
  if (Number(form.value.stock_quantity) < 0) next.stock_quantity = 'Склад не може бути від’ємним.'
  if (!Number(form.value.category_id)) next.category_id = 'Оберіть категорію.'
  if (
    form.value.product_type === 'digital' &&
    !form.value.avatar_frame_id &&
    !form.value.avatar_frame_file &&
    !form.value.digital_asset_url?.trim() &&
    pickedFiles.value.length === 0
  ) {
    next.avatar_frame_id =
      'Оберіть рамку аватара або вкажіть URL цифрового активу, або додайте зображення.'
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
.editor {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 14px;
}

.panel {
  border: 1px solid color-mix(in srgb, var(--border) 55%, transparent);
  border-radius: 14px;
  padding: 14px;
  background: color-mix(in srgb, var(--muted) 72%, transparent);
}

.field {
  display: grid;
  gap: 6px;
  margin-bottom: 10px;
}

.label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--muted-foreground);
}

.native-select,
.native-file {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--background);
  color: var(--foreground);
  padding: 10px 12px;
  font: inherit;
}

.row.two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.switcher {
  margin: 6px 0 12px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.upload-block {
  display: grid;
  gap: 6px;
  margin-bottom: 10px;
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

.preview-title {
  margin: 0 0 8px;
  font-weight: 700;
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
  height: 180px;
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

.summary {
  margin-top: 10px;
  border-top: 1px dashed var(--border);
  padding-top: 8px;
}

.error {
  color: var(--destructive);
  font-size: 0.8rem;
}

.file-name {
  font-size: 0.8rem;
  color: var(--primary);
  font-weight: 600;
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

  .row.two {
    grid-template-columns: 1fr;
  }
}
</style>
