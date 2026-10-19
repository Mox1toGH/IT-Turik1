<template>
  <ui-skeleton-loader :loading="loading">
    <template #skeleton>
      <div class="assignments-grid">
        <ui-card v-for="i in 4" :key="`skeleton-${i}`" class="assignment-skeleton">
          <ui-skeleton variant="rect" width="60%" height="20px" />
          <ui-skeleton variant="rect" width="30%" height="16px" />
          <ui-skeleton variant="rect" width="100%" height="14px" />
          <ui-skeleton variant="rect" width="80%" height="14px" />
        </ui-card>
      </div>
    </template>

    <template #default>
      <ui-card v-if="assignments.length === 0" class="empty-card">
        <p class="empty-text">No assignments found for selected filters</p>
      </ui-card>

      <div v-else class="assignments-grid">
        <evaluation-assignment-card
          v-for="assignment in assignments"
          :key="assignment.id"
          :assignment="assignment"
          @evaluated="$emit('evaluated')"
        />
      </div>
    </template>
  </ui-skeleton-loader>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import EvaluationAssignmentCard from './EvaluationAssignmentCard.vue'
import type { JuryAssignmentResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  assignments: JuryAssignmentResponse[]
  loading?: boolean
}

withDefaults(defineProps<Props>(), { loading: false })

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

.assignment-skeleton {
  background: var(--subtle);
}

.empty-card {
  border-color: var(--border);
}

.empty-text {
  margin: 0;
  color: var(--muted-foreground);
  text-align: center;
  padding: 0.8rem 0;
}
</style>