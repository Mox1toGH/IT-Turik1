<template>
  <ui-card class="tournament-card" :is-error="isError">
    <template #header>
      <div class="tournament-header">
        <h2>Tournament Info</h2>

        <ui-button v-if="tournament?.status === 'draft'" size="sm" @click="handleStartRegistration"
          ><loading-icon v-if="isPending" />Start registration</ui-button
        >
      </div>
    </template>

    <template #error>
      <div style="display: flex; height: 300px; justify-content: center; align-items: center">
        <p>Error while fetching tournament info (code: {{ tournamentInfoError?.code }})</p>
      </div>
    </template>

    <div class="tournament-info">
      <div class="tournament-name">
        <p class="text-muted">Name</p>
        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 0.3rem">
              <ui-skeleton variant="rect" width="100%" />
              <ui-skeleton variant="rect" width="80%" />
            </div>
          </template>

          <p :title="tournament?.name">{{ truncateText(tournament?.name ?? '', 200) }}</p>
        </ui-skeleton-loader>
      </div>

      <div class="tournament-description">
        <p class="text-muted">Description</p>

        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 0.4rem">
              <ui-skeleton variant="rect" width="90%" />
              <ui-skeleton variant="rect" width="70%" />
              <ui-skeleton variant="rect" width="80%" />
            </div>
          </template>

          <large-text-modal
            v-model="isDesciptionOpen"
            title="Tournament description"
            :text="tournament?.description ?? ''"
            max-length="190"
          >
            <template #trigger="{ toggleOpen }">
              <p
                :title="tournament?.description"
                @click="toggleOpen"
                :class="['tournament-description-text', { large: isDescriptionLarge }]"
              >
                {{ truncateText(tournament?.description ?? '', 190) }}
              </p>
            </template>
          </large-text-modal>
        </ui-skeleton-loader>
      </div>

      <div class="tournament-dates">
        <div>
          <p class="text-muted">Start / end date</p>
          <div class="">
            <ui-skeleton-loader :loading="isLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="180px" />
              </template>

              <p>
                {{
                  tournament?.start_date
                    ? formatDate(tournament.start_date, { showHours: true })
                    : '-'
                }}
              </p>
              <p>
                {{
                  tournament?.end_date ? formatDate(tournament.end_date, { showHours: true }) : '-'
                }}
              </p>
            </ui-skeleton-loader>
          </div>
        </div>

        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="100px" />
          </template>

          <ui-badge :variant="statusBadgeVariant">{{ tournament?.status }}</ui-badge>
        </ui-skeleton-loader>
      </div>

      <div class="tournament-points">
        <p class="text-muted">Your points</p>
        <ui-skeleton-loader :loading="pointsLoading">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 0.3rem">
              <ui-skeleton variant="rect" width="120px" />
              <ui-skeleton variant="rect" width="180px" />
            </div>
          </template>

          <div v-if="pointsError" class="points-error">
            <p>Unable to load your points.</p>
          </div>
          <div v-else-if="!profile?.id">
            <p>Log in to see your points balance.</p>
          </div>
          <div v-else>
            <p><strong>Balance:</strong> {{ pointsBalance?.balance ?? 0 }}</p>
            <p v-if="tournamentPointsEarned !== null">
              <strong>From this tournament:</strong>
              <span :class="{ 'positive-value': tournamentPointsEarned > 0 }">
                {{ tournamentPointsEarned > 0 ? '+' : '' }}{{ tournamentPointsEarned }}
              </span>
            </p>
          </div>
        </ui-skeleton-loader>
      </div>
    </div>

    <div class="tournament-action">
      <!-- TODO add link to round info -->
      <ui-button v-if="currentRound" variant="ghost" class="tournament-action-btn">
        Current round: {{ currentRound.name }}
      </ui-button>

      <join-tournament-btn
        v-if="tournament?.status === 'registration'"
        :tournament-id="props.tournamentId"
        :registered-team-id="tournament?.registered_team?.id ?? null"
      />
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { computed, ref } from 'vue'
import { truncateText } from '@/lib/utils'
import { formatDate } from '@/lib/date'
import JoinTournamentBtn from './JoinTournamentBtn.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import LargeTextModal from '../../../../components/shared/LargeTextModal.vue'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useGetMyPointsBalance, useListMyPointsTransactions } from '@/api/points/points'
import {
  useGetCurrentTask,
  useGetTournament,
  useStartTournamentRegistration,
} from '@/api/tournaments/tournaments'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const isDesciptionOpen = ref(false)

const {
  data: tournament,
  isLoading,
  error: tournamentInfoError,
  isError,
} = useGetTournament(props.tournamentId)
const { data: profile } = useGetUserProfile()
const { data: currentRound } = useGetCurrentTask(
  { tournament_id: props.tournamentId },
  {
    query: { enabled: computed(() => tournament.value?.status === 'running') },
  },
)

const {
  data: pointsBalance,
  isLoading: isBalanceLoading,
  error: pointsBalanceError,
} = useGetMyPointsBalance({
  query: { enabled: computed(() => Boolean(profile.value?.id)) },
})
const {
  data: pointsTransactions,
  isLoading: isTransactionsLoading,
  error: pointsTransactionsError,
} = useListMyPointsTransactions(
  { page_size: 100, ordering: '-created_at' },
  {
    query: { enabled: computed(() => Boolean(profile.value?.id) && Boolean(tournament.value)) },
  },
)

const pointsLoading = computed(() => isBalanceLoading.value || isTransactionsLoading.value)
const pointsError = computed(() =>
  Boolean(pointsBalanceError.value || pointsTransactionsError.value),
)
const tournamentPointsEarned = computed(() => {
  if (!tournament.value?.name || !pointsTransactions.value?.results) return null

  return pointsTransactions.value.results
    .filter((transaction) => transaction.reason?.includes(tournament.value?.name))
    .reduce((sum, transaction) => sum + (transaction.amount ?? 0), 0)
})

const isDescriptionLarge = computed(() => (tournament.value?.description.length ?? 0) > 190)
const statusBadgeVariant = computed(() => {
  if (tournament.value?.status === 'draft') return 'gray'
  if (tournament.value?.status === 'finished') return 'gray'
  if (tournament.value?.status === 'running') return 'green'
  if (tournament.value?.status === 'registration') return 'orange'

  return 'gray'
})

const { mutate: startRegistration, isPending } = useStartTournamentRegistration()

const handleStartRegistration = () => {
  startRegistration({
    id: props.tournamentId,
  })
}
</script>

<style scoped>
.tournament-card {
  flex: 1;
}

.tournament-header {
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-timeline {
  display: flex;
  gap: 0.3rem;
}

.tournament-info {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.tournament-name,
.tournament-dates,
.tournament-description {
  padding-bottom: 0.7rem;
  border-bottom: 1px solid var(--border);
}

.tournament-description-text {
  border-radius: 6px;
  transition: background 2s ease-in;
  word-break: break-word;
}

.tournament-dates {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tournament-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.7rem;
}

.tournament-action {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tournament-action-btn {
  width: 100%;
}

.tournament-points {
  padding-top: 0.7rem;
}

.positive-value {
  color: var(--success);
}
</style>
