<template>
  <ui-empty-card
    v-if="assignments.length === 0"
    message="No assignments found for selected filters."
  />
  <div v-else class="assignments-grid">
    <evaluation-assignment-card
      v-for="assignment in assignments"
      :key="assignment.id"
      :assignment="assignment"
      @evaluated="$emit('evaluated')"
    />
  </div>
</template>

<script setup lang="ts">
import UiEmptyCard from '@/components/ui/UiEmptyCard'
import EvaluationAssignmentCard from './EvaluationAssignmentCard.vue'
import type { JuryAssignmentResponse } from '@/api/backendAPINinja.schemas'

defineProps<{
  assignments: JuryAssignmentResponse[]
}>()

defineEmits<{
  (e: 'evaluated'): void
}>()
</script>

<style scoped>
.assignments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.85rem;
}

</style>
