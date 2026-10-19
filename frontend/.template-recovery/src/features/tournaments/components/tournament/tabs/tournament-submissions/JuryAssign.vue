<template>
  <ui-section
    title="Assign jury"
    description="Assign jury members to evaluate round submissions."
    class="jury-assign-shell"
  >
    <ui-card :query="cardQuery" empty-text="No submissions to evaluate yet">
      <template #empty-action>
        <p class="text-sm text-muted">Assignments appear once teams submit to the closed round.</p>
      </template>

      <template #header>
        <div class="submissions-header">
          <ui-skeleton-loader :loading="isLoadingRound">
            <template #skeleton>
              <ui-skeleton variant="rect" width="150px" />
            </template>

            <h2 v-if="closedRound">Round: "{{ closedRound.name }}"</h2>
            <h2 v-else class="text-muted no-closed-round">No round with closed submissions</h2>
          </ui-skeleton-loader>
          <div class="header-actions">
            <ui-select
              multiple
              v-model="assignJuryForAll"
              :options="juryOptions"
              placeholder="Assign jury to all"
              class="jury-select jury-select-all"
              :is-error="isFailedToFetchJury"
              :error="juryFetchError?.message"
              :is-loading="isFetchingJury"
              :disabled="isLoading || noClosedRound || props.tournamentStatus === 'finished'"
            />
            <ui-button
              variant="secondary"
              @click="applyJuryToAllSubmissions"
              :disabled="isLoading || noClosedRound || props.tournamentStatus === 'finished'"
            >
              Apply to all
            </ui-button>
            <ui-button
              @click="handleAssignJury"
              class="assign-btn"
              :disabled="isLoading || noClosedRound || props.tournamentStatus === 'finished'"
            >
              <loading-icon v-if="isPending" />Assign
            </ui-button>
          </div>
        </div>
      </template>

      <template #skeleton>
        <div class="submissions-table">
          <div class="table-head">
            <span>Team</span>
            <span>Submitted On</span>
            <span>Assigned Jury</span>
            <span style="text-align: end">Actions</span>
          </div>

          <div v-for="i in 2" :key="`skeleton-${i}`" class="table-row">
            <div class="team-cell">
              <div class="team-avatar">
                <ui-skeleton variant="rounded" width="40px" height="40px" />
              </div>
              <div class="skeleton-lines">
                <ui-skeleton variant="rect" width="100px" />
                <ui-skeleton variant="rect" width="140px" />
              </div>
            </div>

            <ui-skeleton variant="rect" width="100px" />
            <ui-skeleton variant="rect" width="100px" />
            <ui-skeleton variant="rect" width="100px" />
          </div>
        </div>
      </template>

      <div class="submissions-table">
        <div class="table-head">
          <span>Team</span>
          <span>Submitted On</span>
          <span>Assigned Jury</span>
          <span style="text-align: end">Actions</span>
        </div>

        <jury-assign-row
          v-for="submission in submissions"
          :key="submission.id"
          :submission="submission"
          v-model:assigned="assignedJury[submission.id]"
          :jury-options="juryOptions"
          :is-failed-to-fetch-jury="isFailedToFetchJury"
          :jury-fetch-error-message="juryFetchError?.message"
          :is-fetching-jury="isFetchingJury"
          :team-abbr="teamAbbr"
          :jury-label="juryLabel"
        />
      </div>
    </ui-card>
  </ui-section>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiSection from '@/components/ui/UiSection'
import UiSelect from '@/components/ui/UiSelect'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import UiSkeleton from '@/components/ui/UiSkeleton'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import JuryAssignRow from './JuryAssignRow.vue'
import { useJuryAssign } from '../../../../composables/useJuryAssign'
import type { TournamentStatus } from '@/api/backendAPINinja.schemas'

interface Props {
  tournamentId: number
  tournamentStatus: TournamentStatus
}

const props = defineProps<Props>()

const {
  closedRound,
  submissions,
  noClosedRound,
  isLoadingRound,
  isLoading,
  cardQuery,
  juryOptions,
  juryFetchError,
  isFetchingJury,
  isFailedToFetchJury,
  assignJuryForAll,
  assignedJury,
  isPending,
  applyJuryToAllSubmissions,
  handleAssignJury,
  juryLabel,
  teamAbbr,
} = useJuryAssign(() => props.tournamentId)
</script>

<style scoped>
.submissions-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.jury-assign-shell {
  min-width: 0;
}

.no-closed-round {
  font-size: var(--text-lg);
}

.submissions-table {
  display: grid;
}

.table-head,
.table-row {
  display: grid;
  grid-template-columns: 2.5fr 2fr 2.3fr 2fr;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.table-head {
  color: var(--muted-foreground);
  font-weight: 700;
  border-bottom: 1px solid var(--border);
}

.table-row {
  border-top: 1px solid var(--border);
}

.table-row:first-child {
  border-top: 0;
}

.team-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.team-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--primary-foreground);
  background: var(--primary);
}

.skeleton-lines {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.jury-select-all {
  min-width: 260px;
}

@media (max-width: 820px) {
  .table-head {
    display: none;
  }

  .table-row {
    grid-template-columns: 1fr;
    row-gap: 0.75rem;
  }
}
</style>