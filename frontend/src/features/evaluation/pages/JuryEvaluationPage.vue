<template>
  <section class="jury-page page-shell">
    <header class="jury-hero">
      <div class="jury-hero-copy">
        <div class="breadcrumb-label">
          <span>Workspace</span>
          <span aria-hidden="true">/</span>
          <span>Jury</span>
        </div>

        <h1 class="text-6xl">My Evaluations</h1>
        <p class="section-subtitle text-xl">Review and evaluate submitted projects.</p>
      </div>

      <div class="hero-actions">
        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="180px" height="64px" />
          </template>

          <ui-card variant="stat" class="jury-stat-card">
            <span class="text-sm">Evaluated:</span>
            <strong class="text-xl">{{ evaluatedCount }} / {{ totalCount }}</strong>
          </ui-card>
        </ui-skeleton-loader>
      </div>
    </header>

    <div class="jury-rule" aria-hidden="true"></div>

    <section class="evaluation-section">
      <header class="page-controls-header">
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
      </header>

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
          <ui-card v-if="pagedAssignments.length === 0" class="empty-card">
            <p class="empty-text">No assignments found for selected filters</p>
          </ui-card>

          <div v-else class="assignments-grid">
            <evaluation-assignment-card
              v-for="assignment in pagedAssignments"
              :key="assignment.id"
              :assignment="assignment"
              @evaluated="refetch"
            />
          </div>

          <ui-pagination
            v-if="totalCount > pageSize"
            v-model="currentPage"
            :total-items="totalCount"
            :page-size="pageSize"
          />
        </template>
      </ui-skeleton-loader>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useListJuryAssignments } from '@/api/evaluation/evaluation'
import { useListTournaments } from '@/api/tournaments/tournaments'
import UiCard from '@/components/ui/UiCard.vue'
import UiPagination from '@/components/ui/UiPagination.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import EvaluationAssignmentCard from '../components/EvaluationAssignmentCard.vue'

const selectedRounds = ref<string[]>([])
const selectedTournamentIds = ref<string[]>([])
const evaluationStatus = ref<'all' | 'evaluated' | 'not_evaluated'>('all')
const currentPage = ref(1)
const pageSize = 10

const { data: assignmentsResponse, isLoading, isError, refetch } = useListJuryAssignments()

const {
  data: tournamentsResponse,
  isLoading: isTournamentsLoading,
  isError: isTournamentsError,
} = useListTournaments(
  computed(() => ({
    page: 1,
    page_size: 200,
  })),
)

const assignments = computed(() => assignmentsResponse.value?.results ?? [])
const tournaments = computed(() => tournamentsResponse.value?.data ?? [])

const evaluationStatusOptions = [
  { value: 'all', label: 'All evaluations' },
  { value: 'evaluated', label: 'Evaluated' },
  { value: 'not_evaluated', label: 'Not evaluated' },
]

const roundOptions = computed(() => {
  const unique = new Map<string, string>()

  assignments.value.forEach((assignment) => {
    unique.set(
      String(assignment.round_details.id),
      assignment.round_details.name ?? `Round #${assignment.round_details.id}`,
    )
  })

  tournaments.value.forEach((tournament) => {
    const rounds = Array.isArray(tournament.rounds) ? tournament.rounds : []
    rounds.forEach((round) => {
      unique.set(String(round.id), round.name ?? `Round #${round.id}`)
    })
  })

  return Array.from(unique.entries()).map(([value, label]) => ({ value, label }))
})

const tournamentOptions = computed(() => {
  const byId = new Map<string, string>()

  tournaments.value.forEach((tournament) => {
    byId.set(String(tournament.id), tournament.name)
  })

  assignments.value.forEach((assignment) => {
    const id = assignment.round_details.tournament
    if (id == null) return
    const key = String(id)
    if (!byId.has(key)) byId.set(key, `Tournament #${key}`)
  })

  return Array.from(byId.entries()).map(([value, label]) => ({ value, label }))
})

const filteredAssignments = computed(() => {
  let list = assignments.value

  if (selectedRounds.value.length) {
    list = list.filter((assignment) =>
      selectedRounds.value.includes(String(assignment.round_details.id)),
    )
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

const pagedAssignments = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredAssignments.value.slice(start, end)
})

const totalCount = computed(() => filteredAssignments.value.length)
const evaluatedCount = computed(
  () => filteredAssignments.value.filter((item) => item.is_evaluated).length,
)
const progressPercent = computed(() =>
  totalCount.value ? Math.round((evaluatedCount.value / totalCount.value) * 100) : 0,
)

watch([selectedRounds, selectedTournamentIds, evaluationStatus], () => {
  currentPage.value = 1
})
</script>

<style scoped>
.jury-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.jury-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.jury-hero-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.jury-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.jury-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

.jury-stat-card {
  display: flex;
}

.jury-stat-card strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.jury-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.jury-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.evaluation-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

@media (max-width: 760px) {
  .jury-page {
    padding: 1rem 1rem 2rem;
  }

  .jury-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .jury-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .jury-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
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
