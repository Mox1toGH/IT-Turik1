<template>
  <ui-button variant="secondary" type="button" @click="openModal">
    {{ criteriaCount > 0 ? `Edit criteria (${criteriaCount})` : 'Add criteria' }}
  </ui-button>

  <ui-modal v-model="isOpen" :maxWidth="'760px'" scrollable @close="closeModal">
    <template #title>
      <h2>Add criteria</h2>
    </template>

    <div class="criteria-panel">
      <ui-card v-if="criteriaCount === 0" class="empty-card">
        <p class="empty-error">No criteria added</p>
      </ui-card>

      <div v-else class="criteria-list">
        <ui-card v-for="criterion in criteriaList" :key="criterion.id" class="criteria-card">
          <template #header>
            <div class="criteria-card-info">
              <div class="criteria-card-title">
                <h3 :title="criterion.name">{{ truncateText(criterion.name, 100) }}</h3>
                <span class="criteria-score">Max {{ criterion.max_score }}</span>
              </div>
              <pre class="criteria-description">{{ criterion.description }}</pre>
            </div>
          </template>

          <template #footer>
            <div class="criteria-card-actions">
              <ui-button
                variant="secondary"
                class="delete-button"
                type="button"
                @click="removeCriterion(criterion.id)"
              >
                Delete
              </ui-button>
            </div>
          </template>
        </ui-card>
      </div>

      <ui-card class="add-criteria">
        <template #header>
          <div class="add-criteria-header">
            <h3>New criterion</h3>
            <p class="hint">Add one criterion at a time to keep scoring simple.</p>
          </div>
        </template>

        <div class="add-criteria-grid">
          <label class="form-item">
            <span class="field-label">Name</span>
            <ui-input v-model="newCriterion.name" placeholder="Backend quality" />
          </label>

          <label class="form-item">
            <span class="field-label">Max score</span>
            <ui-input
              type="number"
              v-model.number="newCriterion.max_score"
              min="1"
              placeholder="10"
            />
          </label>

          <label class="form-item full-width">
            <span class="field-label">Description</span>
            <ui-text-area
              v-model="newCriterion.description"
              placeholder="Short description of what judges should assess"
            />
          </label>
        </div>

        <template #footer>
          <div class="button-row">
            <ui-button type="button" @click="addCriterion">Add criterion</ui-button>
          </div>
        </template>
      </ui-card>
    </div>
  </ui-modal>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiTextArea from '@/components/ui/UiTextArea.vue'
import { truncateText } from '@/lib/utils'

interface RoundCriteriaItem {
  id: string
  name: string
  description: string
  max_score: number
}

const emit = defineEmits<{
  (e: 'blur'): void
}>()

const modelValue = defineModel<RoundCriteriaItem[]>({ default: () => [] })

const isOpen = ref(false)
const criteriaList = computed(() => modelValue.value ?? [])
const criteriaCount = computed(() => criteriaList.value.length)

const newCriterion = ref<Omit<RoundCriteriaItem, 'id'>>({
  name: '',
  description: '',
  max_score: 1,
})

function openModal() {
  isOpen.value = true
}

function closeModal() {
  isOpen.value = false
  emit('blur')
}

function addCriterion() {
  const name = newCriterion.value.name.trim()
  const description = newCriterion.value.description.trim()
  const maxScore = Number(newCriterion.value.max_score)

  if (!name || !description || maxScore < 1) return

  modelValue.value = [
    ...criteriaList.value,
    {
      id: crypto.randomUUID(),
      name,
      description,
      max_score: maxScore,
    },
  ]

  newCriterion.value = { name: '', description: '', max_score: 1 }
  emit('blur')
}

function removeCriterion(id: string) {
  modelValue.value = criteriaList.value.filter((criterion) => criterion.id !== id)
  emit('blur')
}
</script>

<style scoped>
.criteria-panel {
  display: grid;
  gap: 1.25rem;
}

.criteria-list {
  display: grid;
  gap: 0.95rem;
}

.criteria-card-info {
  display: grid;
  gap: 0.45rem;
}

.criteria-card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.criteria-card-title h3 {
  font-size: 1rem;
}

.criteria-score {
  color: var(--muted-foreground);
  font-size: 0.92rem;
  white-space: nowrap;
}

.criteria-description {
  color: var(--foreground);
  line-height: 1.6;
  font-size: 0.95rem;
  overflow-x: auto;
  max-width: 100%;
}

.criteria-card-actions {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
}

.delete-button {
  padding: 0.55rem 0.85rem;
}

.add-criteria {
  background: var(--muted);
}

.add-criteria-header {
  display: grid;
  gap: 0.35rem;
}

.add-criteria-header h3 {
  font-size: 1rem;
}

.hint {
  color: var(--muted-foreground);
  font-size: 0.9rem;
  line-height: 1.5;
}

.add-criteria-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
}

.field-label {
  color: var(--muted-foreground);
  font-size: 0.82rem;
  font-weight: 600;
}

.full-width {
  grid-column: 1 / -1;
}

.button-row {
  display: flex;
  justify-content: flex-end;
}

ui-input,
ui-button {
  width: 100%;
}

@media (max-width: 780px) {
  .criteria-card {
    grid-template-columns: 1fr;
  }

  .criteria-card-actions {
    justify-content: flex-start;
  }

  .add-criteria-grid {
    grid-template-columns: 1fr;
  }
}
</style>
