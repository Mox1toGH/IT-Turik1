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

      <div class="team-label">
        <p>Team</p>

        <ui-skeleton-loader :loading="isTeamsLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="60px" />
          </template>

          <p class="text-muted">
            {{ filteredTeams.length }} team{{ filteredTeams.length === 1 ? '' : 's' }}
          </p>
        </ui-skeleton-loader>
      </div>

      <div class="teams-list">
        <ui-skeleton-loader :loading="isTeamsLoading">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 0.4rem">
              <ui-skeleton v-for="i in 4" :key="i" variant="rect" height="48px" width="100%" />
            </div>
          </template>

          <template v-if="filteredTeams.length">
            <div v-for="team in filteredTeams" :key="team.id" class="team-row">
              <RouterLink :to="`/teams/${team.id}`" class="team-item">
                <div class="team-info">
                  <TeamIcon />
                  {{ team.name }}
                  <ui-badge v-if="!team.is_active" variant="red"> Disqualified </ui-badge>
                </div>

                <div style="display: flex; align-items: center; gap: 0.5rem">
                  <ui-badge variant="primary"> {{ team.members_count }} members </ui-badge>
                  <div v-if="isAdmin" class="team-actions">
                    <ui-button
                      v-if="team.is_active"
                      size="sm"
                      variant="danger"
                      :disabled="isUpdating"
                      @click.prevent="openDisqualifyModal(team)"
                    >
                      <TeamDeleteIcon />
                    </ui-button>
                    <ui-button
                      v-else
                      size="sm"
                      variant="default"
                      :disabled="isUpdating"
                      @click.prevent="openReactivateModal(team)"
                    >
                      <AddTeamIcon />
                    </ui-button>
                  </div>
                </div>
              </RouterLink>
            </div>
          </template>

          <p v-else class="text-muted">No teams found.</p>
        </ui-skeleton-loader>
      </div>
    </div>

    <ui-confirm-modal
      v-model="showConfirmModal"
      :title="confirmModalTitle"
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
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import TeamIcon from '@/icons/TeamIcon.vue'
import { RouterLink } from 'vue-router'
import { parseApiError } from '@/api/errors'
import { useRegisteredTeams, useUpdateRegistration } from '@/api/queries/tournaments'
import { useProfile } from '@/api/queries/accounts'
import UiButton from '@/components/ui/UiButton.vue'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import type { GetRegisteredTeamsResponse } from '@/api/services/tournaments/types'
import TeamDeleteIcon from '@/icons/TeamDeleteIcon.vue'
import AddTeamIcon from '@/icons/AddTeamIcon.vue'
import { truncateText } from '@/lib/utils'

interface Props {
  tournamentId: number
}

type Team = GetRegisteredTeamsResponse[number]

const props = defineProps<Props>()

const search = ref('')

const {
  data: teams,
  isLoading: isTeamsLoading,
  error: teamsError,
  isError,
} = useRegisteredTeams({ id: props.tournamentId })
const error = computed(() => parseApiError(teamsError.value))

const filteredTeams = computed(() => {
  if (!teams.value) return []
  const term = search.value.trim().toLowerCase()
  if (!term) return teams.value

  return teams.value.filter((team) => team.name.toLowerCase().includes(term))
})
const { data: user } = useProfile()
const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.role === 'organizer')

const showConfirmModal = ref(false)
const confirmModalTitle = ref('')
const confirmModalConfirmText = ref('')
const confirmModalVariant = ref<'default' | 'danger'>('default')
const disqualificationReason = ref('')
const pendingAction = ref<{ team: Team; action: 'activated' | 'disqualified' } | null>(null)

const { mutate: updateRegistration, isPending: isUpdating } = useUpdateRegistration()

const openDisqualifyModal = (team: Team) => {
  pendingAction.value = { team, action: 'disqualified' }
  disqualificationReason.value = ''
  confirmModalTitle.value = `Disqualify ${truncateText(team.name, 10)}`
  confirmModalConfirmText.value = 'Disqualify'
  confirmModalVariant.value = 'danger'
  showConfirmModal.value = true
}

const openReactivateModal = (team: Team) => {
  pendingAction.value = { team, action: 'activated' }
  confirmModalTitle.value = `Reactivate ${truncateText(team.name, 10)}`
  confirmModalConfirmText.value = 'Reactivate'
  confirmModalVariant.value = 'default'
  showConfirmModal.value = true
}

const handleConfirmAction = () => {
  if (!pendingAction.value) return

  const isDisqualifying = pendingAction.value.action === 'disqualified'

  updateRegistration(
    {
      tournamentId: props.tournamentId,
      registrationId: pendingAction.value.team.registration_id,
      body: {
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
  border-bottom: 1px solid var(--border);
  padding: 0.7rem 10px 0.7rem 0;
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

.team-row {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--border);
}

.team-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.7rem 10px 0.7rem 0;
  text-decoration: none;
  color: inherit;
}

.team-item:hover {
  background: var(--accent);
}

.team-actions {
  display: flex;
  justify-content: flex-end;
  padding: 0.5rem 0;
  gap: 0.5rem;
}
</style>
