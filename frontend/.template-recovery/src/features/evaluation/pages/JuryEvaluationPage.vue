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

      <assignment-grid
        :assignments="pagedAssignments"
        :loading="isLoading"
        @evaluated="refetch"
      />

      <ui-pagination
        v-if="totalCount > pageSize"
        v-model="currentPage"
        :total-items="totalCount"
        :page-size="pageSize"
      />
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useListJuryAssignments } from '@/api/evaluation/evaluation'
import { useListTournaments } from '@/api/tournaments/tournaments'
import UiPagination from '@/components/ui/UiPagination'
import UiSelect from '@/components/ui/UiSelect'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import AssignmentGrid from '../components/AssignmentGrid.vue'
import {
  EVALUATION_STATUS_OPTIONS,
  useEvaluationFilters,
} from '../composables/useEvaluationFilters'

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

const assignments = computed(() => assignmentsResponse.value?.items ?? [])
const tournaments = computed(() => tournamentsResponse.value?.data ?? [])

const evaluationStatusOptions = EVALUATION_STATUS_OPTIONS

const {
  selectedRounds,
  selectedTournamentIds,
  evaluationStatus,
  currentPage,
  pageSize,
  roundOptions,
  tournamentOptions,
  pagedAssignments,
  totalCount,
  evaluatedCount,
  progressPercent,
} = useEvaluationFilters(assignments, tournaments)
</script>

<style scoped>
.jury-page {
  gap: 1.4rem;
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
  color: var(--muted-foreground);
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

.jury-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--border);
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
  background: var(--track);
}

.progress-value {
  height: 100%;
  background: var(--primary);
  transition: width 0.2s ease;
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