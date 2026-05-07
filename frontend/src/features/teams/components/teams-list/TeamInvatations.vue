<template>
  <ui-card :is-error="isLoadingError">
    <template #error>
      <div style="display: flex; height: 136px; justify-content: center; align-items: center">
        <p>Error while fetching invitations (code: {{ error?.code }})</p>
      </div>
    </template>

    <template #header>
      <div class="section-head">
        <h2>Invitations</h2>
        <ui-skeleton-loader :loading="inboxLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="70px" />
          </template>

          <span class="text-muted">{{ pendingInboxInvitations?.length ?? 0 }} pending</span>
        </ui-skeleton-loader>
      </div>
    </template>

    <ui-skeleton-loader :loading="inboxLoading">
      <template #skeleton>
        <div class="team-grid">
          <ui-card class="team-item" v-for="i in 2" :key="i">
            <template #header>
              <div class="team-meta">
                <ui-skeleton variant="rect" width="100%" />
                <ui-skeleton variant="rect" width="80px" />
              </div>
            </template>

            <ui-skeleton variant="rect" width="120px" />

            <template #footer>
              <div style="display: flex; gap: 10px">
                <ui-skeleton variant="rect" height="1.8rem" width="80px" />
                <ui-skeleton variant="rect" height="1.8rem" width="80px" />
              </div>
            </template>
          </ui-card>
        </div>
      </template>

      <p v-if="pendingInboxInvitations?.length === 0" class="text-muted">No pending invitations.</p>
      <div v-else class="team-grid">
        <ui-card
          v-for="invitation in pendingInboxInvitations"
          :key="`invite-${invitation.id}`"
          class="team-item"
        >
          <template #header>
            <div class="team-meta">
              <h3>{{ invitation.team.name }}</h3>

              <ui-badge class="text-muted">
                Invited by: {{ invitation.invited_by?.username || 'Unknown user' }}
              </ui-badge>
            </div>
          </template>

          <template #footer>
            <div class="row-actions">
              <ui-button
                size="sm"
                :disabled="loadingIds.has(invitation.id)"
                @click="respondToInvitation(invitation.id, 'accept')"
              >
                <loading-icon v-if="loadingIds.has(invitation.id)" />
                Accept
              </ui-button>
              <ui-button
                size="sm"
                variant="secondary"
                :disabled="loadingIds.has(invitation.id)"
                @click="respondToInvitation(invitation.id, 'decline')"
              >
                Decline
              </ui-button>
            </div>
          </template>
        </ui-card>
      </div>
    </ui-skeleton-loader>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useNotification } from '@/composables/useNotification'
import { useInvitations, useRespondToInvitation } from '@/api/queries/teams'
import type { InvitationId } from '@/api/dbTypes'
import { computed, ref } from 'vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import { parseApiError } from '@/api/errors'

const { showNotification } = useNotification()

const {
  data: inboxInvitations,
  isLoading: inboxLoading,
  isLoadingError,
  error: invitationsError,
} = useInvitations()
const error = computed(() => parseApiError(invitationsError.value))

const pendingInboxInvitations = computed(() =>
  inboxInvitations.value?.filter((invitation) => invitation.status === 'invited'),
)

const { mutate: respond } = useRespondToInvitation()

const loadingIds = ref<Set<InvitationId>>(new Set())

const respondToInvitation = (invitationId: InvitationId, action: 'accept' | 'decline') => {
  loadingIds.value.add(invitationId)
  respond(
    { id: invitationId, action },
    {
      onSuccess: () => {
        showNotification(
          action === 'accept' ? 'Invitation accepted.' : 'Invitation declined.',
          'success',
        )
      },
      onError: (err) => {
        showNotification(parseApiError(err)?.message, 'error')
      },
      onSettled: () => {
        loadingIds.value.delete(invitationId)
      },
    },
  )
}
</script>

<style scoped>
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.9rem;
}

.team-item {
  padding: 0.95rem;
  background: var(--muted);
  color: var(--muted-foreground);
}

.team-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.team-meta h3 {
  font-family: var(--font-display);
}

.row-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
</style>
