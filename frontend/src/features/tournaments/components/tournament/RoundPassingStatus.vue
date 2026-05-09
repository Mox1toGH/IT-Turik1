<template>
  <section class="round-passing-status">
    <ui-card v-if="!isAdmin">
      <div class="no-access">
        <p>You don't have permission to view passing status.</p>
      </div>
    </ui-card>

    <ui-card v-else>
      <template #header>
        <div class="header">
          <div>
            <h3>Passing Status</h3>
            <p class="text-muted">Team rankings and advancement status.</p>
          </div>

          <ui-badge :variant="roundBadgeVariant">
            {{ roundBadgeText }}
          </ui-badge>
        </div>
      </template>

      <div class="content">
        <div class="passing-info">
          <h4 v-if="passingCount">{{ `Top ${passingCount} teams advance` }}</h4>
          <h4 v-else>All teams advance</h4>
        </div>

        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <div class="results-list">
              <div v-for="i in 5" :key="i" class="result-row skeleton-row">
                <ui-skeleton variant="rect" width="30px" height="20px" />
                <ui-skeleton variant="rect" width="150px" height="20px" />
                <ui-skeleton variant="rect" width="80px" height="24px" />
                <ui-skeleton variant="rect" width="60px" height="20px" />
                <ui-skeleton variant="rect" width="60px" height="20px" />
                <ui-skeleton variant="rect" width="100px" height="32px" />
              </div>
            </div>
          </template>

          <div v-if="isError" class="error-state">
            <div class="error-content">
              <p>{{ error?.message || 'Failed to load passing status.' }}</p>
              <ui-button @click="handleRetry" size="sm" variant="secondary">
                Try Again
              </ui-button>
            </div>
          </div>

          <div v-else-if="!results.length" class="empty-state">
            <p>No results available yet.</p>
          </div>

          <div v-else class="results-list">
            <div
              v-for="(result, index) in sortedResults"
              :key="result.registration_id"
              class="result-row"
              :class="{ 'cut-line': shouldShowCutLine(index) }"
            >
              <div class="rank">#{{ result.rank }}</div>
              <div class="team-name">{{ result.team_name }}</div>
              <div class="badges">
                <ui-badge :variant="getStatusVariant(result)">
                  {{ getStatusText(result) }}
                </ui-badge>
              </div>
              <div class="score">{{ formatScore(result.total_score) }}</div>
              <div class="score">{{ formatScore(result.average_score) }}</div>
              <div class="actions">
                <ui-button
                  v-if="result.is_active"
                  size="sm"
                  variant="danger"
                  :disabled="isUpdating"
                  @click="openDisqualifyModal(result)"
                >
                  Disqualify
                </ui-button>
                <ui-button
                  v-else
                  size="sm"
                  variant="secondary"
                  :disabled="isUpdating"
                  @click="openReactivateModal(result)"
                >
                  Reactivate
                </ui-button>
              </div>
            </div>
          </div>
        </ui-skeleton-loader>
      </div>
    </ui-card>

    <ui-confirm-modal
      v-model="showConfirmModal"
      :title="confirmModalTitle"
      :message="confirmModalMessage"
      :confirm-text="confirmModalConfirmText"
      :confirm-variant="confirmModalVariant"
      :loading="isUpdating"
      @confirm="handleConfirmAction"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { usePassingStatus, useUpdateRegistration } from '@/api/queries/tournaments'
import { useTournamentRounds } from '@/api/queries/tournaments'
import { useProfile } from '@/api/queries/accounts'
import type { PassingStatusResult } from '@/api/services/tournaments/types'

interface Props {
  roundId: number
  tournamentId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  hide: []
}>()

const { data: user } = useProfile()
const isAdmin = computed(() => user.value?.role === 'admin')

const { data: passingStatusData, isLoading, isError, error, refetch } = usePassingStatus(
  { roundId: props.roundId },
  {
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
    enabled: isAdmin
  }
)
const { data: roundsData } = useTournamentRounds({ id: props.tournamentId })

// Watch for round status changes and hide component if needed
watch(() => currentRound.value?.status, (newStatus) => {
  if (newStatus && !['submission_closed', 'evaluated'].includes(newStatus)) {
    emit('hide')
  }
})

const results = computed(() => passingStatusData.value ?? [])

const currentRound = computed(() =>
  roundsData.value?.find(round => round.id === props.roundId)
)

const passingCount = computed(() => currentRound.value?.passing_count ?? null)

const roundBadgeText = computed(() => {
  const status = currentRound.value?.status
  return status === 'evaluated' ? 'Final' : 'Preliminary'
})

const roundBadgeVariant = computed(() => {
  return roundBadgeText.value === 'Final' ? 'green' : 'gray'
})

const sortedResults = computed(() => {
  return [...results.value].sort((a, b) => a.rank - b.rank)
})

const shouldShowCutLine = (index: number) => {
  if (!passingCount.value) return false
  const result = sortedResults.value[index]
  const nextResult = sortedResults.value[index + 1]
  return result?.passed && nextResult && !nextResult.passed
}

const getStatusText = (result: PassingStatusResult) => {
  if (!result.is_active) return 'Disqualified'
  if (!passingCount.value) return 'Advances'
  return result.passed ? 'Advances' : 'Eliminated'
}

const getStatusVariant = (result: PassingStatusResult): 'green' | 'red' | 'gray' => {
  if (!result.is_active) return 'red'
  if (!passingCount.value) return 'green'
  return result.passed ? 'green' : 'red'
}

const showConfirmModal = ref(false)
const confirmModalTitle = ref('')
const confirmModalMessage = ref('')
const confirmModalConfirmText = ref('')
const confirmModalVariant = ref<'primary' | 'danger'>('primary')
const pendingAction = ref<{ result: PassingStatusResult; action: 'activated' | 'disqualified' } | null>(null)

const { mutate: updateRegistration, isPending: isUpdating } = useUpdateRegistration()

const openDisqualifyModal = (result: PassingStatusResult) => {
  pendingAction.value = { result, action: 'disqualified' }
  confirmModalTitle.value = 'Disqualify Team'
  confirmModalMessage.value = `Are you sure you want to disqualify "${result.team_name}"? This action can be reversed.`
  confirmModalConfirmText.value = 'Disqualify'
  confirmModalVariant.value = 'danger'
  showConfirmModal.value = true
}

const openReactivateModal = (result: PassingStatusResult) => {
  pendingAction.value = { result, action: 'activated' }
  confirmModalTitle.value = 'Reactivate Team'
  confirmModalMessage.value = `Are you sure you want to reactivate "${result.team_name}"?`
  confirmModalConfirmText.value = 'Reactivate'
  confirmModalVariant.value = 'primary'
  showConfirmModal.value = true
}

const handleConfirmAction = () => {
  if (!pendingAction.value) return

  updateRegistration({
    tournamentId: props.tournamentId,
    registrationId: pendingAction.value.result.registration_id,
    action: pendingAction.value.action,
  }, {
    onSuccess: () => {
      showConfirmModal.value = false
      pendingAction.value = null
    },
    onError: () => {
      showConfirmModal.value = false
      pendingAction.value = null
    }
  })
}

const handleRetry = () => {
  refetch()
}

function formatScore(value: number) {
  if (Number.isNaN(value)) return '0'
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value)
}
</script>

<style scoped>
.round-passing-status {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.passing-info {
  text-align: center;
  padding: 1rem;
  background: var(--secondary);
  border-radius: var(--radius);
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.result-row {
  display: grid;
  grid-template-columns: 60px 1fr 120px 100px 100px 120px;
  gap: 1rem;
  align-items: center;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
  transition: background-color 0.2s;
}

.result-row.cut-line {
  border-bottom: 2px solid var(--destructive);
  margin-bottom: 1rem;
  position: relative;
}

.result-row.cut-line::after {
  content: 'Cut Line';
  position: absolute;
  bottom: -0.5rem;
  left: 50%;
  transform: translateX(-50%);
  background: var(--destructive);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius);
  font-size: 0.75rem;
  font-weight: 700;
}

.rank {
  font-weight: 700;
  color: var(--foreground);
}

.team-name {
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badges {
  display: flex;
  gap: 0.5rem;
}

.score {
  text-align: right;
  font-weight: 600;
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.skeleton-row {
  opacity: 0.7;
}

.error-state,
.empty-state {
  display: flex;
  height: 200px;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.error-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.no-access {
  display: flex;
  height: 200px;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--muted-foreground);
}

@media (max-width: 768px) {
  .result-row {
    grid-template-columns: 50px 1fr 100px;
    gap: 0.5rem;
  }

  .score {
    display: none;
  }

  .actions {
    grid-column: span 3;
    justify-content: center;
    margin-top: 0.5rem;
  }

  .team-name {
    font-size: 0.9rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
