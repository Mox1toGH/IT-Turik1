<template>
  <ui-modal v-model="isOpen" maxWidth="980px" scrollable>
    <template #title>
      <div class="modal-title">
        <p class="section-eyebrow">Shop workspace</p>
        <h2>{{ product?.name }}</h2>
      </div>
    </template>

    <div v-if="product" class="editor">
      <div class="editor-form">
        <ui-card variant="form" class="form-panel">
          <div class="panel-header">
            <span class="step-marker">01</span>
            <div>
              <h3>Overview</h3>
              <p class="text-muted">What this product is and what it costs.</p>
            </div>
          </div>

          <p class="desc-text">{{ product.description || 'No description' }}</p>

          <div class="row two">
            <ui-card variant="inset" class="summary-list-item">
              <span>Price</span>
              <strong>{{ product.price }} pts</strong>
            </ui-card>
            <ui-card variant="inset" class="summary-list-item">
              <span>Stock</span>
              <strong>{{ product.stock_quantity }}</strong>
            </ui-card>
          </div>
        </ui-card>

        <ui-card v-if="images.length" variant="form" class="form-panel">
          <div class="panel-header">
            <span class="step-marker">02</span>
            <div>
              <h3>Images</h3>
              <p class="text-muted">Tap an image to preview it full size.</p>
            </div>
          </div>

          <div class="preview-grid">
            <article v-for="image in images" :key="image" class="preview-tile">
              <img :src="image" alt="Product image" @click="emit('preview', image)" />
            </article>
          </div>
        </ui-card>

        <ui-card variant="form" class="form-panel">
          <div class="panel-header">
            <span class="step-marker">{{ images.length ? '03' : '02' }}</span>
            <div>
              <h3>Purchase</h3>
              <p class="text-muted">Choose how many you'd like to redeem.</p>
            </div>
          </div>

          <label class="field">
            <span class="label">Quantity</span>
            <ui-number-input v-model="quantity" :min="1" :max="maxQuantity" />
          </label>
        </ui-card>
      </div>

      <aside class="summary-panel" aria-label="Purchase summary">
        <ui-card variant="stat" class="summary-stat">
          <strong>{{ total }}</strong>
          <span>Points to deduct</span>
        </ui-card>

        <ui-card variant="form" class="summary-card">
          <p class="section-eyebrow">Live preview</p>

          <article class="mock-card" :class="{ inactive: !product.is_available }">
            <img
              v-if="cover"
              :src="cover"
              alt="cover"
              class="cover"
              @click="emit('preview', cover)"
            />
            <div v-else class="cover cover-empty">No image</div>
            <div class="mock-content">
              <strong class="mock-name" :title="product.name">
                {{ truncateText(product.name, 100) }}
              </strong>
              <p class="mock-meta">{{ product.category?.name }} | {{ product.product_type }}</p>
              <p class="mock-price">{{ product.price }} pts</p>
            </div>
          </article>

          <div class="summary-list">
            <ui-card variant="inset" class="summary-list-item">
              <span>Current balance</span>
              <strong>{{ balance }}</strong>
            </ui-card>
            <ui-card variant="inset" class="summary-list-item">
              <span>Will deduct</span>
              <strong>{{ total }}</strong>
            </ui-card>
            <ui-card variant="inset" class="summary-list-item">
              <span>Availability</span>
              <strong>{{ product.is_available ? 'Available' : 'Out of stock' }}</strong>
            </ui-card>
          </div>
        </ui-card>
      </aside>
    </div>

    <template #footer>
      <div class="footer-actions">
        <ui-button variant="secondary" :disabled="submitting" @click="isOpen = false">
          Cancel
        </ui-button>
        <ui-button :disabled="submitting || !product?.is_available" @click="submit">
          {{ submitting ? 'Processing...' : 'Buy' }}
        </ui-button>
      </div>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiNumberInput from '@/components/ui/UiNumberInput.vue'
import { getProductImage } from '../../lib/getProductImage'
import { truncateText } from '@/lib/utils'
import type { Product } from '@/api/.ts.schemas'

const props = withDefaults(
  defineProps<{
    product: Product | null
    balance?: number
    submitting?: boolean
  }>(),
  { balance: 0, submitting: false },
)

const emit = defineEmits<{
  purchase: [payload: { productId: number; quantity: number }]
  preview: [url: string]
}>()

const isOpen = defineModel<boolean>({ default: false })

const quantity = ref(1)

watch(
  () => [isOpen.value, props.product?.id],
  () => {
    quantity.value = 1
  },
)

const images = computed(() => {
  if (!props.product) return []
  if (props.product.images?.length) return props.product.images.map((image) => image.image)
  const fallback = getProductImage(props.product)
  return fallback ? [fallback] : []
})

const cover = computed(() => images.value[0] || '')
const maxQuantity = computed(() => Math.max(1, props.product?.stock_quantity || 0))
const total = computed(() => (Number(quantity.value) || 1) * (props.product?.price ?? 0))

const submit = () => {
  if (!props.product) return
  emit('purchase', { productId: props.product.id, quantity: Number(quantity.value) || 1 })
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

.desc-text {
  margin: 0;
  color: var(--foreground);
  word-break: break-word;
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

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  gap: 8px;
}

.preview-tile img {
  width: 100%;
  height: 86px;
  border-radius: 9px;
  object-fit: cover;
  cursor: zoom-in;
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

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
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
