<template>
  <ui-card
    class="tournament-card"
    :status="status"
    :is-fetching="isFetching"
    :is-stale="isStale"
    :error-code="errorCode"
    @retry="refetch"
  >
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
      <div class="info-row">
        <p class="text-muted">Name</p>
        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 0.3rem">
              <ui-skeleton variant="rect" width="100%" />
              <ui-skeleton variant="rect" width="80%" />
            </div>
          </template>

          <ui-truncate :text="tournament?.name ?? ''" />
        </ui-skeleton-loader>
      </div>

      <div class="info-row">
        <p class="text-muted">Description</p>

        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 0.4rem">
              <ui-skeleton variant="rect" width="90%" />
              <ui-skeleton variant="rect" width="70%" />
              <ui-skeleton variant="rect" width="80%" />
            </div>
          </template>

          <ui-expandable-text :text="tournament?.description ?? ''" :lines="3" />
        </ui-skeleton-loader>
      </div>

      <div class="info-row">
        <div class="dates-row">
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

      <div class="info-row limits-row">
        <div>
          <p class="text-muted">Minimum team members</p>
          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100px" />
            </template>

            <p>
              {{
                tournament?.min_team_members
                  ? `${tournament.min_team_members} members`
                  : 'No minimum'
              }}
            </p>
          </ui-skeleton-loader>
        </div>

        <div>
          <p class="text-muted">Maximum teams</p>
          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100px" />
            </template>

            <p>
              {{ tournament?.max_teams ?? 'No limit' }}
              <span v-if="tournament?.max_teams">teams</span>
            </p>
          </ui-skeleton-loader>
        </div>
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
        <p v-if="!isTeamsError && !canManageRegistration && !registeredTeamId">
          You cannot register for this tournament
        </p>
        <p v-if="isTeamsError && !registeredTeamId" class="team-registration-reason" role="alert">
          Failed to load teams. Please try again.
        </p>
        <div v-if="!registeredTeamId && canManageRegistration" class="join-controls">
          <ui-button :disabled="!canJoinSelectedTeam" @click="handleJoin">
            <loading-icon v-if="isRegistering" />
            Join Tournament
          </ui-button>
          <ui-select
            v-model="selectedTeamId"
            :options="teamOptions"
            placeholder="Select a team"
            min-width="220px"
            :is-loading="isLoadingTeams"
            :is-error="isTeamsError"
            error="Failed to fetch teams"
          />
        </div>
        <ui-button
          v-if="registeredTeamId"
          variant="danger"
          :disabled="isLeaving"
          @click="handleLeave"
        >
          <loading-icon v-if="isLeaving" />
          <span>Leave Tournament</span>
        </ui-button>
      </template>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiExpandableText from '@/components/ui/UiExpandableText'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import UiTruncate from '@/components/ui/UiTruncate'
import { computed, ref } from 'vue'
import { formatDate } from '@/lib/date'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useNotification } from '@/composables/useNotification'
import { useCardState } from '@/composables/useCardState'
import { useGetUserProfile } from '@/api/accounts/accounts'
import UiSelect from '@/components/ui/UiSelect'
import {
  useGetCurrentTask,
  useGetTournament,
  useRegisterTeamForTournament,
  useStartTournamentRegistration,
  useListEligibleTeamsForTournament,
  useUnregisterTeamFromTournament,
} from '@/api/tournaments/tournaments'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const selectedTeamId = ref<number | null>(null)

const { showNotification } = useNotification()
const { data: user } = useGetUserProfile()

const tournamentQuery = useGetTournament(props.tournamentId)
const { data: tournament, isLoading, isFetching, refetch } = tournamentQuery
const { status, errorCode, isStale } = useCardState(tournamentQuery)
const { data: currentRound } = useGetCurrentTask(
  { tournament_id: props.tournamentId },
  {
    query: { enabled: computed(() => tournament.value?.status === 'running') },
  },
)

const {
  data: teams,
  isLoading: isLoadingTeams,
  isError: isTeamsError,
} = useListEligibleTeamsForTournament(props.tournamentId)
const { mutate: register, isPending: isRegistering } = useRegisterTeamForTournament()
const { mutate: leave, isPending: isLeaving } = useUnregisterTeamFromTournament()

const registeredTeamId = computed(() => tournament.value?.registered_team?.id ?? null)
const teamOptions = computed(() =>
  (teams.value ?? []).map((team) => ({
    value: team.id,
    label: team.name,
    disabled: !!team.reason,
    reason: team.reason,
  })),
)
const selectedTeam = computed(() => teams.value?.find((team) => team.id === selectedTeamId.value))
const canJoinSelectedTeam = computed(
  () => !!selectedTeam.value && !selectedTeam.value.reason && !isRegistering.value,
)

const canManageRegistration = computed(
  () => user.value?.role === 'team' && ((teams.value?.length ?? 0) > 0 || !!registeredTeamId.value),
)

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

function handleJoin() {
  if (!canJoinSelectedTeam.value || !selectedTeamId.value) return
  register(
    { id: props.tournamentId, data: { team_id: selectedTeamId.value } },
    { onError: (error) => showNotification(error?.message, 'error') },
  )
}
</script>

<style scoped>
.tournament-card {
  flex: 1;
  min-width: 0;
}

.tournament-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.tournament-header h2 {
  margin: 0.5rem 0 0.45rem;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.tournament-header .section-subtitle {
  margin: 0;
}

.tournament-info {
  display: flex;
  flex-direction: column;
}

.info-row {
  padding: 0.8rem 0;
  border-top: 1px solid var(--border);
}

.info-row:first-child {
  border-top: 0;
  padding-top: 0;
}

.info-row p {
  margin: 0;
}

.info-row > .text-muted {
  margin-bottom: 0.45rem;
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 700;
}

.dates-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.limits-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.limits-row p {
  margin: 0;
}

.limits-row .text-muted {
  margin-bottom: 0.45rem;
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 700;
}

.tournament-action {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-top: 0.8rem;
  border-top: 1px solid var(--border);
}

.join-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.team-registration-reason {
  margin: 0;
  color: var(--destructive);
  font-size: var(--text-sm);
}

.tournament-action-btn {
  width: 100%;
}

.positive-value {
  color: var(--success);
}

@media (max-width: 700px) {
  .tournament-header,
  .dates-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .join-controls {
    align-items: stretch;
    flex-direction: column-reverse;
  }
}
</style>
