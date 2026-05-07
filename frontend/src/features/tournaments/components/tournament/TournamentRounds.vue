<template>
  <div class="actions" v-if="user?.role === 'admin'">
    <ui-button asLink :to="`/tournaments/${props.tournamentId}/rounds/create`"
      >Create round</ui-button
    >
  </div>

  <section>
    <ui-skeleton-loader :loading="isLoading">
      <template #skeleton>
        <div class="rounds-list">
          <ui-card v-for="i in 3" :key="i" class="round-card">
            <template #header>
              <div class="round-header">
                <ui-skeleton variant="rect" width="180px" height="24px" />
                <ui-skeleton variant="rect" width="80px" height="24px" />
              </div>
            </template>

            <div style="display: flex; flex-direction: column; gap: 0.3rem">
              <ui-skeleton variant="rect" width="220px" />
              <ui-skeleton variant="rect" width="220px" />
            </div>

            <div class="round-actions">
              <ui-skeleton variant="rect" width="110px" height="36px" />
            </div>
          </ui-card>
        </div>
      </template>

      <ui-card v-if="isError">
        <div style="display: flex; height: 300px; justify-content: center; align-items: center">
          <p>Error while fetching rounds (code: {{ error?.code }})</p>
        </div>
      </ui-card>

      <ui-card v-else-if="rounds.length === 0" class="empty-card">
        <p class="empty-error">No rounds found</p>
      </ui-card>

      <div v-else class="rounds-list">
        <ui-card v-for="round in rounds" :key="round.id" class="round-card">
          <template #header>
            <div class="round-header">
              <h4>{{ truncateText(round.name, 70) }}</h4>
              <ui-badge :variant="badgeVariant(round.status)">{{ round.status }}</ui-badge>
            </div>
          </template>

          <div class="round-dates">
            <p class="text-muted">Start: {{ formatDate(round.start_date, { showHours: true }) }}</p>
            <p class="text-muted">End: {{ formatDate(round.end_date, { showHours: true }) }}</p>
          </div>

          <div class="round-actions">
            <ui-button size="sm" variant="secondary" @click="openDetails(round)">
              View details
            </ui-button>

            <ui-button size="sm" @click="openSubmissionForm"> Submit </ui-button>
            <submit-modal
              :roundId="selectedRound?.id ?? 0"
              :tournamentId="props.tournamentId"
              v-model="isSubmitOpen"
            />

            <ui-button
              v-if="profile?.role === 'admin'"
              size="sm"
              variant="danger"
              @click="handleDeleteRound(round.id)"
            >
              <delete-icon width="20" height="20" />
            </ui-button>
          </div>
        </ui-card>
      </div>
    </ui-skeleton-loader>

    <round-details-modal
      v-if="selectedRound"
      v-model="isDetailsOpen"
      :title="selectedRound?.name ?? ''"
      :description="selectedRound?.description ?? {}"
      :mustHave="selectedRound?.must_have_requirements ?? {}"
      :technicalRequirements="selectedRound?.tech_requirements ?? {}"
    />
  </section>
</template>

<script setup lang="ts">
import { parseApiError } from '@/api/errors'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { truncateText } from '@/lib/utils'
import { formatDate } from '@/lib/date'
import { computed, ref } from 'vue'
import type { Variants } from '@/components/ui/UiBadge.vue'
import { useProfile } from '@/api/queries/accounts'
import RoundDetailsModal from './modals/RoundDetailsModal.vue'
import { useDeleteRound, useTournamentRounds } from '@/api/queries/tournaments'
import type { GetRoundsResponse } from '@/api/services/tournaments/types'
import type { RoundId } from '@/api/dbTypes'
import { useNotification } from '@/composables/useNotification'
import DeleteIcon from '@/icons/DeleteIcon.vue'
import SubmitModal from './modals/SubmitModal.vue'

interface Props {
  tournamentId: number
}
type Round = GetRoundsResponse[number]

const props = defineProps<Props>()
const { showNotification } = useNotification()
const { data: user } = useProfile()

const { data: profile } = useProfile()
const {
  data,
  isLoading,
  error: roundsError,
  isError,
} = useTournamentRounds({ id: props.tournamentId })

const { mutate: deleteRound } = useDeleteRound({ id: props.tournamentId })

const error = computed(() => parseApiError(roundsError.value))
const rounds = computed(() => data.value ?? [])

const isDetailsOpen = ref(false)
const isSubmitOpen = ref(false)
const selectedRound = ref<Round | null>(null)

function handleDeleteRound(id: RoundId) {
  deleteRound(
    {
      id,
    },
    {
      onError: (error) => {
        const parsedError = parseApiError(error)
        showNotification(parsedError?.message, 'error')
      },
    },
  )
}

function openDetails(round: Round) {
  selectedRound.value = round
  isDetailsOpen.value = true
}

function openSubmissionForm() {
  isSubmitOpen.value = !isSubmitOpen.value
}

function badgeVariant(status: Round['status']): Variants {
  if (status === 'active') return 'primary'
  if (status === 'evaluated') return 'green'
  if (status === 'submission_closed') return 'gray'
  return 'gray'
}
</script>

<style scoped>
.actions {
  display: flex;
  justify-content: end;
  align-items: center;
}

.rounds-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
}

.round-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
}

.round-actions {
  display: flex;
  justify-content: end;
  align-items: center;
  gap: 8px;
}

.round-dates {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.round-card {
  min-width: 0;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.description-card {
  grid-column: 1 / 3;
}

.details-editor {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.75rem;
  background: var(--input);
  height: min(60vh, 520px);
  overflow: auto;
}

.details-editor :deep(.ProseMirror) {
  outline: none;
  min-height: 100%;
}

@media (max-width: 900px) {
  .details-grid {
    grid-template-columns: 1fr;
  }

  .description-card {
    grid-column: 1;
  }
}

@media (max-width: 1024px) {
  .rounds-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .rounds-list {
    grid-template-columns: 1fr;
  }
}
</style>
