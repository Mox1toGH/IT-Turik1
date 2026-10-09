<template>
  <div class="filters-wrapper">
    <div class="search-wrapper">
      <ui-input
        v-model="searchInput"
        class="search-input"
        placeholder="Search tournament by name"
        @keydown.enter="applySearch"
      />

      <ui-button
        v-if="searchInput.length >= 2"
        class="search-button"
        aria-label="Search tournaments"
        @click="applySearch"
      >
        <arrow-right />
      </ui-button>
    </div>

    <div class="filters">
      <ui-select
        v-model="status"
        :options="statusOptions"
        placeholder="All statuses"
        :multiple="true"
        align-to="right"
        min-width="120px"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import ArrowRight from '@/icons/ArrowRight.vue'
import type { TournamentStatus } from '@/api/backendAPINinja.schemas'

const status = defineModel<TournamentStatus[]>('status', { required: true })

defineProps<{
  statusOptions: { label: string; value: string }[]
}>()

const emit = defineEmits<{
  search: [query: string]
}>()

const searchInput = ref('')

const applySearch = () => emit('search', searchInput.value.trim())
</script>

<style scoped>
.filters-wrapper {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.8rem;
  align-items: center;
}

.filters {
  display: flex;
  gap: 0.4rem;
  justify-content: end;
}

.search-wrapper {
  display: flex;
  gap: 0.45rem;
  min-width: 0;
}

.search-input {
  flex: 1;
  min-width: 0;
}

.search-button {
  flex: 0 0 auto;
}

@media (max-width: 760px) {
  .filters-wrapper {
    grid-template-columns: 1fr;
  }
}
</style>
