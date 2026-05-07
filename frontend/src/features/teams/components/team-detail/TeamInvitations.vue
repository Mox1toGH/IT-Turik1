<template>
  <ui-card :is-error="isLoadingError">
    <template #error>
      <div style="display: flex; justify-content: center; align-items: center; height: 200px">
        <p>Failed to fetch invitations</p>
      </div>
    </template>

    <section class="team-invitations-section">
      <header class="team-invitations-subhead">
        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="90px" />
          </template>

          <h3>Invitations</h3>
        </ui-skeleton-loader>

        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="130px" />
          </template>

          <span class="text-muted">
            {{ filteredPendingInvitations.length }} awaiting response
            <span v-if="filteredDeclinedInvitations.length">
              , {{ filteredDeclinedInvitations.length }} declined
            </span>
          </span>
        </ui-skeleton-loader>
      </header>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div class="team-invitations-list">
            <ui-card v-for="i in 2" :key="i" class="card-item">
              <div style="display: flex; flex-direction: column; gap: 4px">
                <div style="display: flex; justify-content: space-between; gap: 10px">
                  <ui-skeleton variant="rect" width="100%" />
                  <ui-skeleton variant="rect" width="70px" />
                </div>

                <ui-skeleton variant="rect" width="200px" />
              </div>
            </ui-card>
          </div>
        </template>

        <p
          v-if="filteredPendingInvitations.length === 0 && filteredDeclinedInvitations.length === 0"
          class="text-muted"
        >
          No invitations yet.
        </p>

        <div v-else class="team-invitations-list">
          <ui-card
            v-for="invitation in filteredPendingInvitations"
            :key="`invitation-pending-${invitation.id}`"
            class="card-item"
          >
            <div>
              <div style="display: flex; justify-content: space-between">
                <p class="team-invitations-name">{{ invitation.user.username }}</p>
                <ui-badge class>invited</ui-badge>
              </div>

              <p class="text-muted team-invitations-email">{{ invitation.user.email }}</p>
            </div>
          </ui-card>

          <ui-card
            v-for="invitation in filteredDeclinedInvitations"
            :key="`invitation-declined-${invitation.id}`"
            class="card-item"
          >
            <template #header>
              <div style="display: flex; justify-content: space-between">
                <p class="team-invitations-name">{{ invitation.user.username }}</p>
                <ui-badge v-if="props.isCaptain" variant="green">Captain</ui-badge>
                <div v-else style="display: flex; gap: 4px">
                  <ui-badge variant="red">Declined</ui-badge>
                  <ui-badge>Invatation</ui-badge>
                </div>
              </div>
            </template>

            <p class="text-muted team-invitations-email">{{ invitation.user.email }}</p>

            <template #footer>
              <div class="row-actions">
                <ui-button
                  variant="secondary"
                  size="sm"
                  :disabled="loadingInvitationIds.has(invitation.id)"
                  @click="resendInvitation(invitation.user.id)"
                >
                  <loading-icon v-if="loadingInvitationIds.has(invitation.id)" />
                  Resend invitation
                </ui-button>
              </div>
            </template>
          </ui-card>
        </div>
      </ui-skeleton-loader>
    </section>
  </ui-card>
</template>

<script setup lang="ts">
import type { Invitation, TeamId, UserId } from '@/api/dbTypes'
import type { GetTeamInfoResponse } from '@/api/services/teams/types'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { useNotification } from '@/composables/useNotification'
import { useResendInvitation, useTeamInvitations } from '@/api/queries/teams'
import { computed, ref } from 'vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'

interface Props {
  teamId: TeamId
  searchFilter?: string
  isCaptain?: boolean
}

const emit = defineEmits<{
  (e: 'updateTeam', newTeamValue: GetTeamInfoResponse): void
}>()

const { showNotification } = useNotification()
const props = defineProps<Props>()

const {
  data: invitations,
  isLoading,
  isLoadingError,
} = useTeamInvitations({ teamId: props.teamId })

const uniqueInvitations = computed(() => {
  const byUserId = new Map<UserId, Invitation>()
  for (const inv of invitations.value ?? []) {
    const uid = inv.user.id

    const prev = byUserId.get(uid)
    if (!prev) {
      byUserId.set(uid, inv)
    }
  }
  return Array.from(byUserId.values())
})

const matches = (parts: (string | undefined)[]) => {
  const q = props.searchFilter?.trim().toLowerCase()
  if (!q) return true
  return parts.some((p) => p?.toLowerCase().includes(q))
}

const filteredPendingInvitations = computed(() =>
  uniqueInvitations.value
    .filter((i) => i.status === 'invited')
    .filter((i) => matches([i.user.username, i.user.email, i.user.full_name])),
)

const filteredDeclinedInvitations = computed(() =>
  uniqueInvitations.value
    .filter((i) => i.status === 'declined')
    .filter((i) => matches([i.user.username, i.user.email, i.user.full_name])),
)

const loadingInvitationIds = ref<Set<UserId>>(new Set())
const { mutate: resendInvitationMutate } = useResendInvitation()

const resendInvitation = (userId: UserId) => {
  loadingInvitationIds.value.add(userId)

  resendInvitationMutate(
    { teamId: props.teamId, body: { user_id: userId } },
    {
      onSuccess: (data) => {
        emit('updateTeam', data)
      },
      onError: (err) => {
        showNotification(
          err.response ? 'Unable to resend invitation.' : 'Server connection error.',
          'error',
        )
      },
      onSettled: () => {
        loadingInvitationIds.value.delete(userId)
      },
    },
  )
}
</script>

<style scoped>
.team-invitations-section {
  display: grid;
  gap: 0.65rem;
}

.team-invitations-subhead {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.8rem;
}

.team-invitations-subhead h3 {
  margin: 0;
  font-size: 1rem;
}

.team-invitations-list {
  overflow-y: auto;
  max-height: 350px;
  display: grid;
  gap: 0.55rem;
  grid-template-rows: auto;
}

.card-item {
  background-color: var(--muted);
}

.team-invitations-name {
  font-weight: 700;
}

.team-invitations-email {
  font-size: 0.84rem;
}

.row-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .team-invitations-meta {
    align-items: flex-start;
  }
}
</style>
