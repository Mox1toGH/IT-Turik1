<template>
  <RouterLink :to="`/teams/${team.id}`" class="team-item">
    <div class="team-info">
      <TeamIcon :class="[{ 'text-muted': !team.is_active }]" />
      <p :title="team.name" :class="[{ 'text-muted': !team.is_active }]">
        {{ truncateText(team.name, 15) }}
      </p>
    </div>

    <div class="team-action-group">
      <template v-if="!isDisqualified">
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
      </template>
      <template v-else>
        <ui-badge variant="red">Disqualified</ui-badge>
        <ui-button
          v-if="
            isAdmin && (tournament?.status === 'registration' || tournament?.status === 'running')
          "
          size="sm"
          variant="default"
          :disabled="isUpdating"
          @click.prevent.stop="openReactivateModal(team)"
        >
          <AddTeamIcon />
        </ui-button>
      </template>
    </div>
  </RouterLink>

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
        placeholder="e.g. Rules violation"
        style="width: 100%"
        autofocus
      />
    </div>
  </ui-confirm-modal>
</template>

<script setup lang="ts">
import { truncateText } from '@/lib/utils'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import { ref } from 'vue'
import { useNotification } from '@/composables/useNotification'
import { useDisqualifyTeamFromTournament } from '@/api/tournaments/tournaments'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import AddTeamIcon from '@/icons/AddTeamIcon.vue'
import UiInput from '@/components/ui/UiInput.vue'
import TeamDeleteIcon from '@/icons/TeamDeleteIcon.vue'
import type { TournamentResponse, TournamentTeamResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  tournament?: TournamentResponse
  team: TournamentTeamResponse
  isAdmin: boolean
  isDisqualified?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  isDisqualified: false,
})

const showConfirmModal = ref(false)
const confirmModalTitle = ref('')
const confirmModalConfirmText = ref('')
const confirmModalConfirmMessage = ref<string | undefined>()
const confirmModalVariant = ref<'default' | 'danger'>('default')
const disqualificationReason = ref('')
const pendingAction = ref<{
  team: TournamentTeamResponse
  action: 'activated' | 'disqualified'
} | null>(null)

const { showNotification } = useNotification()
const { mutate: updateRegistration, isPending: isUpdating } = useDisqualifyTeamFromTournament()

function openDisqualifyModal(team: TournamentTeamResponse) {
  pendingAction.value = { team, action: 'disqualified' }
  disqualificationReason.value = ''
  confirmModalTitle.value = `Disqualify ${truncateText(team.name, 10)}`
  confirmModalConfirmText.value = 'Disqualify'
  confirmModalVariant.value = 'danger'
  showConfirmModal.value = true
}

function openReactivateModal(team: TournamentTeamResponse) {
  pendingAction.value = { team, action: 'activated' }
  confirmModalTitle.value = `Reactivate ${truncateText(team.name, 10)}`
  confirmModalConfirmText.value = 'Reactivate'
  confirmModalConfirmMessage.value = 'Are you sure you want to reactivate this team?'
  confirmModalVariant.value = 'default'
  showConfirmModal.value = true
}

function handleConfirmAction() {
  if (!pendingAction.value || !props.tournament) return

  const isDisqualifying = pendingAction.value.action === 'disqualified'

  updateRegistration(
    {
      id: props.tournament.id,
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
      onError: (error) => {
        showConfirmModal.value = false
        pendingAction.value = null

        showNotification(error.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.team-info {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  min-width: 0;
}

.team-info p {
  margin: 0;
  overflow-wrap: anywhere;
}

.team-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
  margin-top: 0.55rem;
  padding: 0.75rem 0.85rem;
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: var(--background);
  color: var(--foreground);
  text-decoration: none;
}

.team-item:hover {
  background: color-mix(in srgb, var(--primary) 5%, transparent);
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
</style>
