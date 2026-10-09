<template>
  <ui-card variant="panel" class="tournament-card" :is-error="isError">
    <template #header>
      <div class="tournament-header">
        <div>
          <p class="section-eyebrow">Overview</p>
          <h2 class="text-3xl">Tournament info</h2>
          <p class="section-subtitle text-base">Core dates, description, and your progress.</p>
        </div>

        <ui-button v-if="tournament?.status === 'draft'" @click="handleStartRegistration">
          <loading-icon v-if="isPending" />
          Start registration
        </ui-button>
      </div>
    </template>

    <template #error>
      <div style="display: flex; height: 300px; justify-content: center; align-items: center">
        <p>Error while fetching tournament info</p>
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
    </div>

    <div class="tournament-action">
      <ui-button
        v-if="currentRound"
        as-link
        :to="`/tournaments/${tournament?.id}?section=rounds`"
        class="tournament-action-btn"
      >
        Current round: {{ currentRound.name }}
      </ui-button>

      <template v-if="tournament?.status === 'registration'">
        <p v-if="!canManageRegistration">You cannot register for this tournament</p>
        <ui-button
          v-if="!registeredTeamId"
          :disabled="!canManageRegistration"
          @click="isTeamModalOpen = true"
        >
          Join Tournament
        </ui-button>

        <ui-button v-else variant="danger" :disabled="isLeaving" @click="handleLeave">
          <loading-icon v-if="isLeaving" />
          <span>Leave Tournament</span>
        </ui-button>

        <team-select-modal v-model="isTeamModalOpen" :tournament-id="tournamentId" />
      </template>
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
import LoadingIcon from '@/icons/LoadingIcon.vue'
import LargeTextModal from '../../../../../components/shared/LargeTextModal.vue'
import TeamSelectModal from './tournament-info/TeamSelectModal.vue'
import { useNotification } from '@/composables/useNotification'
import { useGetUserProfile } from '@/api/accounts/accounts'
import {
  useGetCurrentTask,
  useGetTournament,
  useStartTournamentRegistration,
  useListEligibleTeamsForTournament,
  useUnregisterTeamFromTournament,
} from '@/api/tournaments/tournaments'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const isDesciptionOpen = ref(false)
const isTeamModalOpen = ref(false)

const { showNotification } = useNotification()
const { data: user } = useGetUserProfile()

const { data: tournament, isLoading, isError } = useGetTournament(props.tournamentId)
const { data: currentRound } = useGetCurrentTask(
  { tournament_id: props.tournamentId },
  {
    query: { enabled: computed(() => tournament.value?.status === 'running') },
  },
)

const { data: teams } = useListEligibleTeamsForTournament(props.tournamentId)
const { mutate: leave, isPending: isLeaving } = useUnregisterTeamFromTournament()

const registeredTeamId = computed(() => tournament.value?.registered_team?.id ?? null)

const canManageRegistration = computed(
  () => user.value?.role === 'team' && ((teams.value?.length ?? 0) > 0 || !!registeredTeamId.value),
)

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

function handleLeave() {
  if (!registeredTeamId.value || isLeaving.value) return
  leave(
    { id: props.tournamentId, data: { team_id: registeredTeamId.value } },
    { onError: (error) => showNotification(error?.message, 'error') },
  )
}
</script>

<style scoped>
.tournament-card {
  flex: 1;
}

.tournament-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.tournament-header h2 {
  margin: 2rem 0 0.45rem;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.tournament-header .section-subtitle {
  margin: 0;
}

.status-timeline {
  display: flex;
  gap: 0.3rem;
}

.tournament-info {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.tournament-name,
.tournament-dates,
.tournament-description {
  padding: 0.95rem;
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: var(--background);
}

.tournament-name p,
.tournament-dates p,
.tournament-description p {
  margin: 0;
}

.tournament-name .text-muted,
.tournament-dates .text-muted,
.tournament-description .text-muted {
  margin-bottom: 0.45rem;
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 700;
}

.tournament-description-text {
  border-radius: 6px;
  transition: background 2s ease-in;
  word-break: break-word;
}

.tournament-dates {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
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

.positive-value {
  color: var(--success);
}

@media (max-width: 700px) {
  .tournament-header,
  .tournament-dates {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
