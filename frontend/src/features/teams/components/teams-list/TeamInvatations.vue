<template>
  <ui-card variant="panel" :isError="isLoadingError">
    <template #error>
      <div style="display: flex; height: 136px; justify-content: center; align-items: center">
        <p>Error while fetching invitations (code: {{ invitationsError?.code }})</p>
      </div>
    </template>

    <template #header>
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Incoming</p>
          <h2 class="text-3xl">Invitations</h2>
          <p class="section-subtitle text-base">Team invitations waiting for your response.</p>
        </div>

        <div class="section-meta">
          <ui-skeleton-loader :loading="inboxLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="90px" height="38px" />
            </template>

            <span class="count-pill text-base"
              >{{ pendingInboxInvitations?.length ?? 0 }} pending</span
            >
          </ui-skeleton-loader>
        </div>
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

      <div v-if="pendingInboxInvitations?.length === 0" class="empty-row">
        <div class="empty-icon" aria-hidden="true">+</div>
        <div class="empty-copy">
          <h3 class="text-lg">No pending invitations</h3>
          <p class="text-base">When someone invites you, it will appear here.</p>
        </div>
        <a class="empty-link text-sm" href="#other-teams">Browse available teams <span>-></span></a>
      </div>

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
import { computed, ref } from 'vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import {
  useAcceptTeamInvitation,
  useDeclineTeamInvitation,
  useListTeamInvitations,
} from '@/api/teams/teams'

const { showNotification } = useNotification()

const {
  data: inboxInvitations,
  isLoading: inboxLoading,
  isLoadingError,
  error: invitationsError,
} = useListTeamInvitations()

const pendingInboxInvitations = computed(() =>
  inboxInvitations.value?.filter((invitation) => invitation.status === 'invited'),
)

const { mutate: accept } = useAcceptTeamInvitation()
const { mutate: decline } = useDeclineTeamInvitation()

const loadingIds = ref<Set<number>>(new Set())

const respondToInvitation = (invitationId: number, action: 'accept' | 'decline') => {
  loadingIds.value.add(invitationId)
  const mutate = action === 'accept' ? accept : decline
  mutate(
    { invitationId: invitationId },
    {
      onSuccess: () => {
        showNotification('Invitation accepted.', 'success')
      },
      onError: (error) => {
        showNotification(error.message, 'error')
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
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.section-head h2 {
  margin: 2rem 0 0.45rem;
  font-family: var(--font-display);
  font-weight: 800;
}

.section-head .section-subtitle {
  margin: 0;
}

.section-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 1rem;
}

.count-pill {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--line-soft);
  border-radius: 999px;
  color: var(--muted-foreground);
  white-space: nowrap;
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

.empty-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-height: 96px;
  padding: 1.35rem;
  border: 1px dashed var(--line-soft);
  border-radius: 16px;
  background: var(--background);
}

.empty-icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--primary) 22%, transparent);
  color: var(--primary);
  font-size: var(--text-2xl);
  font-weight: 800;
}

.empty-copy {
  min-width: 0;
  flex: 1;
}

.empty-copy h3,
.empty-copy p {
  margin: 0;
}

.empty-copy h3 {
  color: var(--foreground);
  font-weight: 800;
}

.empty-copy p {
  margin-top: 0.25rem;
  color: var(--muted-foreground);
}

.empty-link {
  color: var(--primary);
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
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

@media (max-width: 700px) {
  .section-head,
  .empty-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .section-meta {
    min-height: 0;
    align-items: flex-start;
  }

  .empty-link {
    white-space: normal;
  }
}
</style>
