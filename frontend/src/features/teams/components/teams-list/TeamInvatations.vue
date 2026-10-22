<template>
  <div class="teams-widget">
    <ui-query-block :query="invitationsQuery" title="invitations">
      <ui-query-field>
        <template #skeleton>
          <div class="team-grid">
            <div class="team-item-skeleton" v-for="i in 2" :key="i">
              <div class="team-skeleton-body">
                <div class="team-meta">
                  <ui-skeleton variant="rect" width="100%" />
                  <ui-skeleton variant="rect" width="80px" />
                </div>

                <ui-skeleton variant="rect" width="120px" />

                <div style="display: flex; gap: 10px">
                  <ui-skeleton variant="rect" height="1.8rem" width="80px" />
                  <ui-skeleton variant="rect" height="1.8rem" width="80px" />
                </div>
              </div>
            </div>
          </div>
        </template>

        <template #default>
          <div v-if="isEmpty" class="empty-text text-muted">
            <p>No invitations. When someone invites you, it will appear here.</p>
            <button type="button" class="empty-link text-sm" @click="emit('browse-teams')">
              Browse available teams <span aria-hidden="true">-&gt;</span>
            </button>
          </div>
          <div v-else class="team-grid">
            <ui-card
              v-for="invitation in pendingInboxInvitations"
              :key="`invite-${invitation.id}`"
              class="team-item"
            >
              <div class="team-body">
                <div class="team-meta">
                  <ui-truncate :text="invitation.team.name" class="team-title" />

                  <ui-badge class="text-muted">
                    Invited by: {{ invitation.invited_by?.username || 'Unknown user' }}
                  </ui-badge>
                </div>
              </div>

              <template #footer>
                <div class="row-actions">
                  <ui-button
                    size="sm"
                    :disabled="loadingIds.has(invitation.id)"
                    @click="respondToInvitation(invitation.id, 'accept')"
                  >
                    <LoaderCircle class="animate-spin" v-if="loadingIds.has(invitation.id)" />
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
        </template>
      </ui-query-field>
    </ui-query-block>
  </div>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiTruncate from '@/components/ui/UiTruncate'
import { useNotification } from '@/composables/useNotification'
import { computed, ref } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiBadge from '@/components/ui/UiBadge'
import {
  useAcceptTeamInvitation,
  useDeclineTeamInvitation,
  useListTeamInvitations,
} from '@/api/teams/teams'

const emit = defineEmits<{
  'browse-teams': []
}>()

const { showNotification } = useNotification()

const invitationsQuery = useListTeamInvitations()
const { data: inboxInvitations } = invitationsQuery

const pendingInboxInvitations = computed(() =>
  inboxInvitations.value?.items.filter((invitation) => invitation.status === 'invited'),
)
const isEmpty = computed(() => pendingInboxInvitations.value?.length === 0)

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
.teams-widget {
  display: grid;
  gap: 1rem;
  min-width: 0;
}

.empty-text {
  display: grid;
  gap: 0.5rem;
  justify-items: center;
  margin: 0;
  padding: 2rem 0;
  text-align: center;
  overflow-wrap: anywhere;
}

.empty-text p {
  margin: 0;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

.team-item {
  height: 100%;
  min-width: 0;
  padding: 0;
  overflow: hidden;
}

.team-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
  padding: 1rem 1.25rem;
}

.team-item-skeleton {
  height: 100%;
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

.team-skeleton-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
}

.empty-link {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--primary);
  font: inherit;
  font-weight: 800;
  cursor: pointer;
}

.empty-link:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
}

.team-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.team-meta h3,
.team-title {
  font-family: var(--font-display);
  margin: 0;
  font-size: 1.1rem;
  font-weight: 800;
  min-width: 0;
}

.row-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.team-item :deep(.card-footer) {
  padding: 0 1.25rem 1.25rem;
}
</style>
