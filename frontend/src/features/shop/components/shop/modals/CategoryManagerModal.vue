<template>
  <ui-modal v-model="isOpen" maxWidth="700px" scrollable>
    <template #title>
      <div class="modal-title">
        <p class="section-eyebrow">Shop workspace</p>
        <h2>Categories</h2>
      </div>
    </template>

    <div class="editor-form">
      <ui-card variant="form" class="form-panel">
        <div class="panel-header">
          <span class="step-marker">01</span>
          <div>
            <h3>Browse</h3>
            <p class="text-muted">Find, rename, or remove an existing category.</p>
          </div>
        </div>

        <div class="row two">
          <label class="field">
            <span class="label">Search</span>
            <ui-input v-model.trim="categorySearch" placeholder="Search categories" />
          </label>
        </div>

        <div class="categories-list">
          <article v-if="!filteredCategories.length" class="categories-empty">
            <p class="text-muted">No categories found.</p>
          </article>

          <article
            v-for="category in filteredCategories"
            :key="category.id"
            class="category-item"
            :class="{ editing: editingCategoryId === category.id }"
          >
            <div class="category-main">
              <label v-if="editingCategoryId === category.id" class="field">
                <span class="label">Name</span>
                <ui-input
                  v-model.trim="editingName"
                  placeholder="Category name"
                  @keyup.enter="saveEdit"
                />
              </label>
              <template v-else>
                <p class="category-name">{{ category.name }}</p>
                <span class="category-id">#{{ category.id }}</span>
              </template>
            </div>

            <div class="row-actions">
              <template v-if="editingCategoryId === category.id">
                <ui-button size="sm" :disabled="!editingName" @click="saveEdit">Save</ui-button>
                <ui-button size="sm" variant="secondary" @click="cancelEdit">Cancel</ui-button>
              </template>
              <template v-else>
                <ui-button size="sm" variant="secondary" @click="startEdit(category)">
                  Edit
                </ui-button>
                <ui-button size="sm" variant="danger" @click="emit('delete', category.id)">
                  Delete
                </ui-button>
              </template>
            </div>
          </article>
        </div>
      </ui-card>

      <ui-card variant="form" class="form-panel">
        <div class="panel-header">
          <span class="step-marker">02</span>
          <div>
            <h3>Create category</h3>
            <p class="text-muted">Add a new category for products to belong to.</p>
          </div>
        </div>

        <form class="category-create-row" @submit.prevent="submitCreate">
          <label class="field">
            <span class="label">Name</span>
            <ui-input v-model.trim="newCategoryName" placeholder="Category name" />
          </label>
          <ui-button type="submit" :disabled="!newCategoryName">Add category</ui-button>
        </form>
      </ui-card>
    </div>

    <template #footer>
      <div class="footer-actions">
        <ui-button variant="secondary" @click="isOpen = false">Done</ui-button>
      </div>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import type { ShopCategory } from '@/api/services/shop/types'

const props = defineProps<{
  categories: ShopCategory[]
}>()

const emit = defineEmits<{
  create: [name: string]
  update: [payload: { id: number; name: string }]
  delete: [id: number]
}>()

const isOpen = defineModel<boolean>({ default: false })

const categorySearch = ref('')
const newCategoryName = ref('')
const editingCategoryId = ref<number | null>(null)
const editingName = ref('')

/* Форма створення та інлайн-редагування більше не ділять один стан. */
watch(isOpen, (open) => {
  if (open) return
  categorySearch.value = ''
  newCategoryName.value = ''
  cancelEdit()
})

const filteredCategories = computed(() => {
  const query = categorySearch.value.trim().toLowerCase()
  if (!query) return props.categories
  return props.categories.filter((category) => category.name.toLowerCase().includes(query))
})

const startEdit = (category: ShopCategory) => {
  editingCategoryId.value = category.id
  editingName.value = category.name
}

const cancelEdit = () => {
  editingCategoryId.value = null
  editingName.value = ''
}

const saveEdit = () => {
  if (editingCategoryId.value === null || !editingName.value) return
  emit('update', { id: editingCategoryId.value, name: editingName.value })
  cancelEdit()
}

const submitCreate = () => {
  if (!newCategoryName.value) return
  emit('create', newCategoryName.value)
  newCategoryName.value = ''
}
</script>

<style scoped>
.modal-title h2 {
  margin: 0.2rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
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
  align-items: end;
}

.categories-list {
  max-height: 320px;
  overflow: auto;
  border-radius: 14px;
  padding: 2px;
  display: grid;
  gap: 8px;
}

.categories-empty {
  display: grid;
  place-items: center;
  min-height: 120px;
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
  align-items: end;
}

.category-main {
  min-width: 0;
  flex: 1;
  display: grid;
  gap: 3px;
}

.category-main .field {
  margin-bottom: 0;
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

.row-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.category-create-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: end;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 900px) {
  .row.two {
    grid-template-columns: 1fr;
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
