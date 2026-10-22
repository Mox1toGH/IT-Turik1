<template>
  <div class="team-item">
    <div class="team-info">
      <Users :class="[{ 'text-muted': !team.is_active }]" :size="28" />
      <RouterLink
        :to="`/teams/${team.id}`"
        :title="team.name"
        :class="[{ 'text-muted': !team.is_active }]"
      >
        {{ team.name }}
      </RouterLink>
    </div>

    <div class="team-action-group">
      <template v-if="!isDisqualified">
        <ui-badge variant="primary">
          {{ team.members_count }} {{ team.members_count === 1 ? 'member' : 'members' }}
        </ui-badge>
        <ui-button
          v-if="isAdmin"
          size="sm"
          variant="danger"
          :disabled="isUpdating"
          aria-label="Disqualify team"
          @click.prevent.stop="openDisqualifyModal(team)"
        >
          <UserX :size="16" />
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
          aria-label="Reactivate team"
          @click.prevent.stop="openReactivateModal(team)"
        >
          <UserPlus :size="20" />
        </ui-button>
      </template>
    </div>
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
        placeholder="e.g. Rules violation"
        style="width: 100%"
        autofocus
      />
    </div>
  </ui-confirm-modal>
</template>

<script setup lang="ts">
import { truncateText } from '@/lib/utils'
import UiConfirmModal from '@/components/ui/UiConfirmModal'
import { ref } from 'vue'
import { useNotification } from '@/composables/useNotification'
import { useDisqualifyTeamFromTournament } from '@/api/tournaments/tournaments'
import UiButton from '@/components/ui/UiButton'
import UiBadge from '@/components/ui/UiBadge'
import { UserPlus, UserX, Users } from 'lucide-vue-next'
import UiInput from '@/components/ui/UiInput'
import type { Tournament, TournamentTeam } from '@/features/tournaments/types'

interface Props {
  tournament?: Tournament
  team: TournamentTeam
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
  team: TournamentTeam
  action: 'activated' | 'disqualified'
} | null>(null)

const { showNotification } = useNotification()
const { mutate: updateRegistration, isPending: isUpdating } = useDisqualifyTeamFromTournament()

function openDisqualifyModal(team: TournamentTeam) {
  pendingAction.value = { team, action: 'disqualified' }
  disqualificationReason.value = ''
  confirmModalTitle.value = `Disqualify ${truncateText(team.name, 10)}`
  confirmModalConfirmText.value = 'Disqualify'
  confirmModalVariant.value = 'danger'
  showConfirmModal.value = true
}

function openReactivateModal(team: TournamentTeam) {
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
  gap: 0.5rem;
  min-width: 0;
  overflow: hidden;
}

.team-info a {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--foreground);
  text-decoration: none;
}

.team-info a:hover {
  text-decoration: underline;
}

.team-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.25rem;
  color: var(--foreground);
  text-decoration: none;
}

.team-action-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}
</style>
