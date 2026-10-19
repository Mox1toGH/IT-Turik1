<template>
  <ui-card
    :status="status"
    :is-fetching="isFetching"
    :is-stale="isStale"
    :error-code="errorCode"
    @retry="refetch"
  >
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
            <div v-for="i in 2" :key="i" class="invitation-row">
              <div style="display: flex; flex-direction: column; gap: 4px; flex: 1">
                <div style="display: flex; justify-content: space-between; gap: 10px">
                  <ui-skeleton variant="rect" width="100%" />
                  <ui-skeleton variant="rect" width="70px" />
                </div>

                <ui-skeleton variant="rect" width="200px" />
              </div>
            </div>
          </div>
        </template>

        <p
          v-if="filteredPendingInvitations.length === 0 && filteredDeclinedInvitations.length === 0"
          class="text-muted"
        >
          No invitations yet.
        </p>

        <div v-else class="team-invitations-list">
          <div
            v-for="invitation in filteredPendingInvitations"
            :key="`invitation-pending-${invitation.id}`"
            class="invitation-row"
          >
            <div class="team-invitations-user">
              <user-avatar
                :avatar="invitation.user.avatar"
                :username="invitation.user.username"
                :full-name="invitation.user.full_name"
                :size="40"
              />
              <div class="invitation-main">
                <div class="invitation-top">
                  <p class="team-invitations-name">{{ invitation.user.username }}</p>
                  <ui-badge>invited</ui-badge>
                </div>

                <p class="text-muted team-invitations-email">{{ invitation.user.email }}</p>
              </div>
            </div>
          </div>

          <div
            v-for="invitation in filteredDeclinedInvitations"
            :key="`invitation-declined-${invitation.id}`"
            class="invitation-row"
          >
            <div class="team-invitations-user">
              <user-avatar
                :avatar="invitation.user.avatar"
                :username="invitation.user.username"
                :full-name="invitation.user.full_name"
                :size="40"
              />
              <div class="invitation-main">
                <div class="invitation-top">
                  <p class="team-invitations-name">{{ invitation.user.username }}</p>
                  <ui-badge v-if="props.isCaptain" variant="green">Captain</ui-badge>
                  <div v-else class="declined-badges">
                    <ui-badge variant="red">Declined</ui-badge>
                    <ui-badge>Invatation</ui-badge>
                  </div>
                </div>
              </div>
            </div>

            <p class="text-muted team-invitations-email">{{ invitation.user.email }}</p>

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
          </div>
        </div>
      </ui-skeleton-loader>
    </section>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import { useCardState } from '@/composables/useCardState'
import { useNotification } from '@/composables/useNotification'
import { computed, ref } from 'vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useInviteMemberToTeam, useListTeamInvitationsByTeam } from '@/api/teams/teams'
import type { TeamInvitationResponse, TeamResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  teamId: number
  searchFilter?: string
  isCaptain?: boolean
}

const emit = defineEmits<{
  (e: 'updateTeam', newTeamValue: TeamResponse): void
}>()

const { showNotification } = useNotification()
const props = defineProps<Props>()

const invitationsQuery = useListTeamInvitationsByTeam(props.teamId)
const { data: invitations, isLoading, isFetching, refetch } = invitationsQuery
const { status, errorCode, isStale } = useCardState(invitationsQuery)

const uniqueInvitations = computed(() => {
  const byUserId = new Map<number, TeamInvitationResponse>()
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

const loadingInvitationIds = ref<Set<number>>(new Set())
const { mutate: resendInvitationMutate } = useInviteMemberToTeam()

const resendInvitation = (userId: number) => {
  loadingInvitationIds.value.add(userId)

  resendInvitationMutate(
    { pk: props.teamId, data: { user_id: userId } },
    {
      onSuccess: (data) => {
        emit('updateTeam', data)
      },
      onError: (error) => {
        showNotification(error?.message, 'error')
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
  gap: 0;
  grid-template-rows: auto;
}

.invitation-row {
  display: grid;
  gap: 0.5rem;
  padding: 0.7rem 0;
}

.team-invitations-list .invitation-row + .invitation-row {
  border-top: 1px solid var(--border);
}

.team-invitations-name {
  margin: 0;
  font-weight: 700;
  overflow-wrap: anywhere;
}

.team-invitations-email {
  margin: 0;
  font-size: 0.84rem;
  overflow-wrap: anywhere;
}

.team-invitations-user {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  min-width: 0;
}

.invitation-main {
  flex: 1;
  min-width: 0;
}

.invitation-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.declined-badges {
  display: flex;
  gap: 4px;
}

.row-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
</style>
