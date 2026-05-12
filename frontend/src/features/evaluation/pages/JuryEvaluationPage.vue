<template>
  <section class="page-shell">
    <div class="section-header">
      <p class="section-eyebrow">Jury</p>
      <h1 class="section-title">My Evaluations</h1>
      <p class="section-subtitle">Review and evaluate submitted projects</p>
    </div>

    <ui-card>
      <template #header>
        <div class="page-controls">
          <div class="filters-wrap">
            <ui-select
              v-model="selectedRounds"
              :options="roundOptions"
              multiple
              min-width="220px"
              placeholder="Filter by round"
              align-to="left"
              :is-loading="isLoading"
              :is-error="isError"
              error="Failed to fetch rounds"
            />
            <ui-select
              v-model="selectedTournamentIds"
              :options="tournamentOptions"
              multiple
              min-width="220px"
              placeholder="Filter by tournament"
              align-to="left"
              :is-loading="isLoading || isTournamentsLoading"
              :is-error="isError || isTournamentsError"
              error="Failed to fetch tournaments"
            />
            <ui-select
              v-model="evaluationStatus"
              :options="evaluationStatusOptions"
              min-width="220px"
              placeholder="Filter by evaluation"
              align-to="left"
              :is-loading="isLoading"
              :is-error="isError"
              error="Failed to fetch assignments"
            />
          </div>

          <div class="progress-wrap">
            <p class="progress-text">{{ evaluatedCount }} / {{ totalCount }} evaluated</p>
            <div class="progress-bar">
              <div class="progress-value" :style="{ width: `${progressPercent}%` }" />
            </div>
          </div>
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
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
          <ui-card v-if="filteredAssignments.length === 0" class="empty-card">
            <p class="empty-text">No assignments found for selected round filters</p>
          </ui-card>

          <div v-else class="assignments-grid">
            <evaluation-assignment-card
              v-for="assignment in filteredAssignments"
              :key="assignment.id"
              :assignment="assignment"
              @evaluated="refetch"
            />
          </div>
        </template>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAssignments } from '@/api/queries/evaluation'
import { useTournaments } from '@/api/queries/tournaments'
import UiCard from '@/components/ui/UiCard.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import EvaluationAssignmentCard from '../components/EvaluationAssignmentCard.vue'

const selectedRounds = ref<string[]>([])
const selectedTournamentIds = ref<string[]>([])
const evaluationStatus = ref<'all' | 'evaluated' | 'not_evaluated'>('all')

const { data: assignments, isLoading, isError, refetch } = useAssignments()
const {
  data: tournamentsResponse,
  isLoading: isTournamentsLoading,
  isError: isTournamentsError,
} = useTournaments({
  page: 1,
  pageSize: 200,
})

const evaluationStatusOptions = [
  { value: 'all', label: 'All evaluations' },
  { value: 'evaluated', label: 'Evaluated' },
  { value: 'not_evaluated', label: 'Not evaluated' },
]

const roundOptions = computed(() => {
  const unique = new Map<string, string>()
  ;(assignments.value ?? []).forEach((assignment) => {
    unique.set(String(assignment.round_details.id), assignment.round_details.name)
  })

  return Array.from(unique.entries()).map(([value, label]) => ({ value, label }))
})

const tournamentOptions = computed(() => {
  const byId = new Map<string, string>()

  ;(tournamentsResponse.value?.data ?? []).forEach((tournament) => {
    byId.set(String(tournament.id), tournament.name)
  })

  ;(assignments.value ?? []).forEach((assignment) => {
    const id = assignment.round_details.tournament
    if (id == null) return
    const key = String(id)
    if (!byId.has(key)) byId.set(key, `Tournament #${key}`)
  })

  return Array.from(byId.entries()).map(([value, label]) => ({ value, label }))
})

const filteredAssignments = computed(() => {
  let list = assignments.value ?? []

  if (selectedRounds.value.length) {
    list = list.filter((assignment) => selectedRounds.value.includes(String(assignment.round_details.id)))
  }

  if (selectedTournamentIds.value.length) {
    list = list.filter((assignment) =>
      selectedTournamentIds.value.includes(String(assignment.round_details.tournament)),
    )
  }

  if (evaluationStatus.value === 'evaluated') {
    list = list.filter((assignment) => assignment.is_evaluated)
  } else if (evaluationStatus.value === 'not_evaluated') {
    list = list.filter((assignment) => !assignment.is_evaluated)
  }

  return list
})

const totalCount = computed(() => filteredAssignments.value.length)
const evaluatedCount = computed(
  () => filteredAssignments.value.filter((item) => item.is_evaluated).length,
)
const progressPercent = computed(() =>
  totalCount.value ? Math.round((evaluatedCount.value / totalCount.value) * 100) : 0,
)
</script>

<style scoped>
.page-shell {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-header {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.section-eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted-foreground);
  font-size: 0.8rem;
}

.section-title {
  margin: 0;
}

.section-subtitle {
  margin: 0;
  color: var(--muted-foreground);
}

.page-controls {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.filters-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.progress-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  width: 280px;
  max-width: 100%;
}

.progress-text {
  margin: 0;
  text-align: right;
  color: var(--muted-foreground);
}

.progress-bar {
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--muted) 70%, transparent);
}

.progress-value {
  height: 100%;
  background: var(--primary);
  transition: width 0.2s ease;
}

.assignments-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.assignment-skeleton {
  background: var(--muted);
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

@media (max-width: 980px) {
  .assignments-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-controls {
    flex-direction: column;
  }

  .filters-wrap {
    width: 100%;
  }

  .progress-wrap {
    width: 100%;
  }

  .progress-text {
    text-align: left;
  }
}
</style>
