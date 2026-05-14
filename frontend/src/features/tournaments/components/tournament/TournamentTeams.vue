<template>
  <ui-card class="tournament-card" :is-error="isError">
    <template #header>
      <h2 class="tournament-card-title">Teams Info</h2>
    </template>

    <template #error>
      <div style="display: flex; height: 300px; justify-content: center; align-items: center">
        <p>Error while fetching tournament teams (code: {{ error?.code }})</p>
      </div>
    </template>

    <div>
      <ui-input
        v-model="search"
        placeholder="Search team"
        class="team-search"
        :disabled="isTeamsLoading"
      />

      <TournamentTeamSection
        sectionType="active"
        :teams="activeTeams"
        :loading="isActiveTeamsLoading"
        :search="search"
      >
        <template #default="{ team }">
          <RouterLink :to="`/teams/${team.id}`" class="team-item">
            <div class="team-info">
              <ui-badge v-if="!team.is_active" variant="red">
                <CrossIcon />
              </ui-badge>
              <TeamIcon :class="[{ 'text-muted': !team.is_active }]" />
              <p :title="team.name" :class="[{ 'text-muted': !team.is_active }]">
                {{ truncateText(team.name, 15) }}
              </p>
            </div>

            <div class="team-action-group">
              <ui-badge variant="primary">{{ team.members_count }} members</ui-badge>
              <ui-button
                v-if="isAdmin"
                size="sm"
                variant="danger"
                :disabled="isUpdating"
                @click.prevent.stop="openDisqualifyModal(team)"
              >
                <TeamDeleteIcon />
              </ui-button>
            </div>
          </RouterLink>
        </template>
      </TournamentTeamSection>

      <TournamentTeamSection
        v-if="hasDisqualifiedTeams"
        sectionType="disqualified"
        :teams="teams"
        :loading="isTeamsLoading"
        :search="search"
      >
        <template #default="{ team }">
          <RouterLink :to="`/teams/${team.id}`" class="team-item">
            <div class="team-info">
              <TeamIcon />
              {{ team.name }}
            </div>

            <div class="team-action-group">
              <ui-badge variant="red">Disqualified</ui-badge>
              <ui-button
                v-if="
                  isAdmin &&
                  (tournament?.status === 'registration' || tournament?.status === 'running')
                "
                size="sm"
                variant="default"
                :disabled="isUpdating"
                @click.prevent.stop="openReactivateModal(team)"
              >
                <AddTeamIcon />
              </ui-button>
            </div>
          </RouterLink>
        </template>
      </TournamentTeamSection>
    </div>

    <ui-confirm-modal
      v-model="showConfirmModal"
      :title="confirmModalTitle"
      :message="confirmModalConfirmMessage"
      :confirm-text="confirmModalConfirmText"
      :confirm-variant="confirmModalVariant"
      :loading="isUpdating"
      @confirm="handleConfirmAction"
    >
      <div v-if="pendingAction?.action === 'disqualified'" class="reason-input form-item">
        <p class="form-label">Reason:</p>
        <ui-input
          v-model="disqualificationReason"
          label="Reason (optional)"
          placeholder="e.g. Violation of rules"
          style="width: 100%"
          autofocus
        />
      </div>
    </ui-confirm-modal>
  </ui-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import TeamIcon from '@/icons/TeamIcon.vue'
import { RouterLink } from 'vue-router'
import UiButton from '@/components/ui/UiButton.vue'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import TournamentTeamSection from './tournament-teams/TournamentTeamSection.vue'
import TeamDeleteIcon from '@/icons/TeamDeleteIcon.vue'
import AddTeamIcon from '@/icons/AddTeamIcon.vue'
import { truncateText } from '@/lib/utils'
import CrossIcon from '@/icons/CrossIcon.vue'
import {
  useDisqualifyTeamFromTournament,
  useGetTournament,
  useListTournamentTeams,
} from '@/api/tournaments/tournaments'
import { useGetUserProfile } from '@/api/accounts/accounts'
import type { TournamentTeamRegistrationList } from '@/api/.ts.schemas'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const search = ref('')

const { data: tournament } = useGetTournament(props.tournamentId)
const {
  data: activeTeams,
  isLoading: isActiveTeamsLoading,
  error: activeTeamsError,
  isError: isActiveTeamsError,
} = useListTournamentTeams(props.tournamentId, { status: 'all' })
const {
  data: teams,
  isLoading: isTeamsLoading,
  error: disqualifiedTeamsError,
  isError: isDisqualifiedTeamsError,
} = useListTournamentTeams(props.tournamentId, { status: 'disqualified' })
const isError = computed(() => isActiveTeamsError.value || isDisqualifiedTeamsError.value)
const error = computed(() => activeTeamsError.value || disqualifiedTeamsError.value)

const hasDisqualifiedTeams = computed(() => (teams.value?.length ?? 0) > 0)
const { data: user } = useGetUserProfile()
const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.role === 'organizer')

const showConfirmModal = ref(false)
const confirmModalTitle = ref('')
const confirmModalConfirmText = ref('')
const confirmModalConfirmMessage = ref<string | undefined>()
const confirmModalVariant = ref<'default' | 'danger'>('default')
const disqualificationReason = ref('')
const pendingAction = ref<{
  team: TournamentTeamRegistrationList
  action: 'activated' | 'disqualified'
} | null>(null)

const { mutate: updateRegistration, isPending: isUpdating } = useDisqualifyTeamFromTournament()

const openDisqualifyModal = (team: TournamentTeamRegistrationList) => {
  pendingAction.value = { team, action: 'disqualified' }
  disqualificationReason.value = ''
  confirmModalTitle.value = `Disqualify ${truncateText(team.name, 10)}`
  confirmModalConfirmText.value = 'Disqualify'
  confirmModalVariant.value = 'danger'
  showConfirmModal.value = true
}

const openReactivateModal = (team: TournamentTeamRegistrationList) => {
  pendingAction.value = { team, action: 'activated' }
  confirmModalTitle.value = `Reactivate ${truncateText(team.name, 10)}`
  confirmModalConfirmText.value = 'Reactivate'
  confirmModalConfirmMessage.value = 'Are you sure you want to reactivate this team?'
  confirmModalVariant.value = 'default'
  showConfirmModal.value = true
}

const handleConfirmAction = () => {
  if (!pendingAction.value) return

  const isDisqualifying = pendingAction.value.action === 'disqualified'

  updateRegistration(
    {
      id: props.tournamentId,
      registrationPk: pendingAction.value.team.registration_id,
      data: {
        action: isDisqualifying ? 'disqualify' : 'reactivate',
        disqualification_reason: isDisqualifying ? disqualificationReason.value : '',
      },
    },
    {
      onSuccess: () => {
        showConfirmModal.value = false
        pendingAction.value = null
        disqualificationReason.value = ''
      },
      onError: () => {
        showConfirmModal.value = false
        pendingAction.value = null
      },
    },
  )
}
</script>

<style scoped>
.tournament-card {
  flex: 1;
}

.tournament-card-title {
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.team-search {
  width: 100%;
  margin-bottom: 1rem;
}

.teams-list-wrap {
  background-color: var(--muted);
}

.team-info {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.team-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border);
  padding: 0.7rem 0;
}

.team-item:hover {
  background: var(--accent);
}

.team-item:not(:last-child) {
  border-bottom: 1px solid var(--border);
}

.team-action-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.team-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.teams-list {
  overflow-y: auto;
  max-height: 400px;
}

.disqualified-wrap {
  margin-top: 1rem;
}

.label-with-icon {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.team-row {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--border);
}
</style>
