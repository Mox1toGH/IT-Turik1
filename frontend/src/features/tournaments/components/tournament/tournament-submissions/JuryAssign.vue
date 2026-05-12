<template>
  <section class="jury-assign-shell">
    <ui-card :is-error="isError">
      <template #error>
        <div style="display: flex; justify-content: center; align-items: center; height: 200px">
          <p>{{ error?.message || 'Something went wrong' }}</p>
        </div>
      </template>

      <template #header>
        <div class="submissions-header">
          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="150px" />
            </template>

            <h2>Round: "{{ closedRound?.name ?? '-' }}"</h2>
          </ui-skeleton-loader>
          <ui-button
            @click="handleAssignJury"
            class="assign-btn"
            :disabled="isLoading || noClosedRound"
          >
            <loading-icon v-if="isPending" />Assign
          </ui-button>
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
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
                <div style="display: flex; flex-direction: column; gap: 8px; flex: 1">
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

          <ui-card v-if="submissions?.length === 0" class="empty-card"
            ><p class="empty-error">No submissions was submited to this round</p></ui-card
          >
          <div v-else v-for="submission in submissions" :key="submission.id" class="table-row">
            <div class="team-cell">
              <div class="team-avatar">{{ teamAbbr(submission.team_details.name) }}</div>
              <div>
                <p class="team-name">{{ submission.team_details.name }}</p>
                <p class="team-meta" :title="submission.description">
                  {{ truncateText(submission.description || 'No description', 25) }}
                </p>
              </div>
            </div>

            <p class="text-muted">{{ formatDate(submission.created_at, { showHours: true }) }}</p>

            <div class="assigned-cell">
              <ui-badge
                v-for="juryId in assignedJury[submission.id] ?? []"
                :key="juryId"
                variant="primary"
              >
                {{ juryLabel(juryId) }}
              </ui-badge>
              <span v-if="!assignedJury[submission.id]?.length" class="empty-state"
                >No jury assigned</span
              >
            </div>

            <div class="actions-cell">
              <ui-select
                multiple
                v-model="assignedJury[submission.id]!"
                :options="juryOptions"
                placeholder="Assign jury"
                class="jury-select"
                :is-error="isFailedToFetchJury"
                :error="parsedJuryError?.message"
                :is-loading="isFetchingJury"
              />
            </div>
          </div>
        </div>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiSelect, { type SelectOption } from '@/components/ui/UiSelect.vue'
import { formatDate } from '@/lib/date'
import UiCard from '@/components/ui/UiCard.vue'
import type { TournamentId } from '@/api/dbTypes'
import { useRoundSubmissions, useTournamentInfo } from '@/api/queries/tournaments'
import { truncateText } from '@/lib/utils'
import { useAssignJury, useAvailableJury } from '@/api/queries/evaluation'
import type { AssignJuryBody } from '@/api/services/evaluation/types'
import UiButton from '@/components/ui/UiButton.vue'
import { useNotification } from '@/composables/useNotification'
import { parseApiError } from '@/api/errors'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'

interface Props {
  tournamentId: TournamentId
}

const props = defineProps<Props>()

const { showNotification } = useNotification()

const {
  data: tournament,
  isLoading: tournamentLoading,
  isError: tournamentError,
  error: tournamentErrorData,
} = useTournamentInfo({ id: props.tournamentId })

const closedRound = computed(() =>
  tournament.value?.rounds.find((round) => round.status === 'submission_closed'),
)

const {
  data: submissions,
  isLoading: submissionsLoading,
  isLoadingError: submissionsError,
  error: submissionsErrorData,
} = useRoundSubmissions(
  {
    roundId: computed(() => closedRound.value?.id ?? 0),
  },
  {
    enabled: computed(() => !!closedRound.value),
  },
)

const {
  data: availableJury,
  isLoading: isFetchingJury,
  isError: isFailedToFetchJury,
  error: juryFetchError,
} = useAvailableJury(
  {
    roundId: computed(() => closedRound.value?.id ?? 0),
  },
  {
    enabled: computed(() => !!closedRound.value),
  },
)
const parsedJuryError = computed(() => parseApiError(juryFetchError.value))

const noClosedRound = computed(() => !!tournament.value && !closedRound.value)
const isLoading = computed(() => tournamentLoading.value || submissionsLoading.value)
const isError = computed(
  () => noClosedRound.value || tournamentError.value || submissionsError.value,
)
const error = computed(() => {
  if (noClosedRound.value) {
    return { message: 'No finished round available' }
  }

  if (tournamentError.value) {
    return (
      parseApiError(tournamentErrorData.value) ?? { message: 'Failed to fetch tournament info' }
    )
  }

  return parseApiError(submissionsErrorData.value) ?? { message: 'Failed to fetch submissions' }
})

const juryOptions = computed<SelectOption[]>(
  () =>
    availableJury.value?.map((jury) => ({
      value: jury.id,
      label: jury.username,
    })) ?? [],
)

const assignedJury = reactive<Record<number, number[]>>({})
watch(
  submissions,
  (value) => {
    if (!value) return
    value.forEach((submission) => {
      const nextAssigned = (submission.assignments ?? [])
        .map((assignment) => assignment.jury?.id)
        .filter((id): id is number => typeof id === 'number')

      assignedJury[submission.id] = Array.from(new Set(nextAssigned))
    })
  },
  { immediate: true },
)

const { mutate: assign, isPending } = useAssignJury()
const handleAssignJury = () => {
  if (!closedRound.value) return
  const payload = submissions.value?.map((submission) => {
    return {
      submission: submission.id,
      jury: assignedJury[submission.id],
    }
  })

  assign(
    {
      roundId: closedRound.value?.id,
      body: payload as unknown as AssignJuryBody,
    },
    {
      onError: (error) => {
        const parsedError = parseApiError(error)
        showNotification(parsedError?.message, 'error')
      },
      onSuccess: () => {
        showNotification('Assigment was sucessfully replaced', 'success')
      },
    },
  )
}

const juryLabel = (value: number) =>
  juryOptions.value.find((option) => option.value === value)?.label ?? String(value)

const teamAbbr = (teamName: string) =>
  teamName
    .split(' ')
    .map((word) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 3)
</script>

<style scoped>
.submissions-header {
  display: flex;
  justify-content: space-between;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.jury-assign-shell {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-header {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.section-eyebrow {
  margin: 0;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted-foreground);
}

.section-title {
  margin: 0;
  font-size: 1.5rem;
}

.section-subtitle {
  margin: 0;
  color: var(--muted-foreground);
  line-height: 1.5;
}

.submissions-table {
  display: grid;
  gap: 0.5rem;
}

.table-head,
.table-row {
  display: grid;
  grid-template-columns: 2.5fr 2fr 2.3fr 2fr;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1rem;
  border-radius: 1rem;
  background: var(--muted);
  border: 1px solid var(--border);
}

.table-head {
  background: transparent;
  border-color: transparent;
  color: var(--muted-foreground);
  font-weight: 700;
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
  color: white;
  background: var(--primary);
}

.team-name {
  margin: 0;
  font-weight: 700;
}

.team-meta {
  margin: 0.15rem 0 0;
  color: var(--muted-foreground);
  font-size: 0.92rem;
}

.assigned-cell {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  min-height: 2.6rem;
}

.empty-state {
  color: var(--muted-foreground);
  font-size: 0.92rem;
}

.actions-cell {
  display: flex;
  justify-content: flex-end;
}

.jury-select {
  min-width: 220px;
}

@media (max-width: 820px) {
  .table-head {
    display: none;
  }

  .table-row {
    grid-template-columns: 1fr;
    row-gap: 0.75rem;
  }

  .actions-cell {
    justify-content: flex-start;
  }
}
</style>
