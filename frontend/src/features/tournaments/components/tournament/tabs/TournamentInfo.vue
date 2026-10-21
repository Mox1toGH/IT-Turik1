<template>
  <ui-card class="tournament-card">
    <template #header>
      <div class="tournament-header">
        <div>
          <p class="section-eyebrow">Overview</p>
          <h2 class="text-3xl">Tournament info</h2>
          <p class="section-subtitle text-base">Core dates, description, and your progress.</p>
        </div>

        <ui-button v-if="tournament?.status === 'draft'" @click="handleStartRegistration">
          <LoaderCircle class="animate-spin" v-if="isPending" />
          Start registration
        </ui-button>
      </div>
    </template>

    <ui-query-state :query="tournamentQuery" title="tournament">
      <template #skeleton>
      <div class="tournament-info">
        <div class="info-section">
          <p class="section-label">Name</p>
          <div class="skeleton-lines">
            <ui-skeleton variant="rect" width="100%" />
            <ui-skeleton variant="rect" width="80%" />
          </div>
        </div>

        <div class="info-section">
          <p class="section-label">Description</p>
          <div class="skeleton-lines">
            <ui-skeleton variant="rect" width="90%" />
            <ui-skeleton variant="rect" width="70%" />
            <ui-skeleton variant="rect" width="80%" />
          </div>
        </div>

        <div class="info-section">
          <p class="section-label">Dates</p>
          <div class="dates-row">
            <div class="dates-values">
              <ui-skeleton variant="rect" width="180px" />
            </div>
            <ui-skeleton variant="rect" width="100px" />
          </div>
        </div>

        <div class="info-section">
          <p class="section-label">Limits</p>
          <div class="limits-row">
            <ui-skeleton variant="rect" width="100px" />
            <ui-skeleton variant="rect" width="100px" />
          </div>
        </div>
      </div>
      </template>

    <div class="tournament-info">
      <div class="info-section">
        <p class="section-label">Name</p>
        <ui-truncate :text="tournament?.name ?? ''" />
      </div>

      <div class="info-section">
        <p class="section-label">Description</p>
        <ui-expandable-text :text="tournament?.description ?? ''" :lines="3" />
      </div>

      <div class="info-section">
        <p class="section-label">Dates</p>
        <div class="dates-row">
          <div class="dates-values">
            <p class="date-value">
              <span class="date-label">Start</span>
              {{
                tournament?.start_date
                  ? formatDate(tournament.start_date, { showHours: true })
                  : '-'
              }}
            </p>
            <p class="date-value">
              <span class="date-label">End</span>
              {{
                tournament?.end_date ? formatDate(tournament.end_date, { showHours: true }) : '-'
              }}
            </p>
          </div>

          <ui-badge :variant="statusBadgeVariant">{{ tournament?.status }}</ui-badge>
        </div>
      </div>

      <div class="info-section">
        <p class="section-label">Limits</p>
        <div class="limits-row">
          <div class="limit-item">
            <p class="limit-value">
              {{
                tournament?.min_team_members
                  ? `${tournament.min_team_members} members`
                  : 'No minimum'
              }}
            </p>
          </div>

          <div class="limit-item">
            <p class="limit-value">
              {{ tournament?.max_teams ?? 'No limit' }}
              <span v-if="tournament?.max_teams">teams</span>
            </p>
          </div>
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
            <LoaderCircle class="animate-spin" v-if="isRegistering" />
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
          <LoaderCircle class="animate-spin" v-if="isLeaving" />
          <span>Leave Tournament</span>
        </ui-button>
      </template>
    </div>
    </ui-query-state>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiQueryState from '@/components/ui/UiQueryState'
import UiExpandableText from '@/components/ui/UiExpandableText'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiTruncate from '@/components/ui/UiTruncate'
import { computed, ref } from 'vue'
import { formatDate } from '@/lib/date'
import { LoaderCircle } from 'lucide-vue-next'
import { useNotification } from '@/composables/useNotification'
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
const { data: tournament } = tournamentQuery
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
  (teams.value?.items ?? []).map((team) => ({
    value: team.id,
    label: team.name,
    disabled: !!team.reason,
    reason: team.reason,
  })),
)
const selectedTeam = computed(() =>
  teams.value?.items.find((team) => team.id === selectedTeamId.value),
)
const canJoinSelectedTeam = computed(
  () => !!selectedTeam.value && !selectedTeam.value.reason && !isRegistering.value,
)

const canManageRegistration = computed(
  () =>
    user.value?.role === 'team' && ((teams.value?.items.length ?? 0) > 0 || !!registeredTeamId.value),
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
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.5rem;
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

.info-section {
  padding: 1.25rem 0;
  border-bottom: 1px solid var(--border);
}

.info-section:first-child {
  padding-top: 0.5rem;
}

.info-section:last-child {
  border-bottom: 0;
  padding-bottom: 0.5rem;
}

.section-label {
  margin: 0 0 0.5rem;
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted-foreground);
}

.dates-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.dates-values {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.date-value {
  margin: 0;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--foreground);
}

.date-label {
  display: inline-block;
  min-width: 2.5rem;
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--muted-foreground);
}

.limits-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.skeleton-lines {
  display: grid;
  gap: 0.35rem;
}

.limit-value {
  margin: 0;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--foreground);
}

.tournament-action {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 1.25rem;
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
