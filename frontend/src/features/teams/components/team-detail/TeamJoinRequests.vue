<template>
  <ui-card :is-error="isLoadingError">
    <template #error>
      <div style="display: flex; justify-content: center; align-items: center; height: 200px">
        <p>Failed to fetch join requests</p>
      </div>
    </template>

    <ui-skeleton-loader :loading="isLoading">
      <template #skeleton>
        <div class="join-requests-section">
          <header class="join-requests-subhead">
            <ui-skeleton variant="rect" width="150px" />
            <ui-skeleton variant="rect" width="50px" />
          </header>

          <div class="join-requests-list">
            <ui-card v-for="i in 2" :key="i" class="card-item">
              <div style="display: flex; flex-direction: column; gap: 5px">
                <ui-skeleton variant="rect" width="200px" />
                <ui-skeleton variant="rect" width="200px" />
              </div>

              <template #footer>
                <div class="row-actions">
                  <ui-skeleton variant="rect" height="30px" width="80px" />
                  <ui-skeleton variant="rect" height="30px" width="80px" />
                </div>
              </template>
            </ui-card>
          </div>
        </div>
      </template>

      <div class="join-requests-list">
        <header class="join-requests-subhead">
          <h3>Join Requests</h3>
          <span class="text-muted">{{ filteredPendingJoinRequests?.length }} pending</span>
        </header>

        <ui-card
          class="card-item"
          v-for="joinRequest in filteredPendingJoinRequests"
          :key="`join-request-${joinRequest.id}`"
        >
          <div class="join-request-user">
            <user-avatar
              :avatar="joinRequest.user.avatar"
              :username="joinRequest.user.username"
              :full-name="joinRequest.user.full_name"
              :size="40"
            />
            <div>
              <p class="join-request-name">{{ joinRequest.user.username }}</p>
              <p class="text-muted join-request-email">{{ joinRequest.user.email }}</p>
            </div>
          </div>

          <template #footer>
            <div>
              <div class="row-actions">
                <ui-button
                  size="sm"
                  :disabled="loadingJoinRequestIds.has(joinRequest.id)"
                  @click="reviewJoinRequest(joinRequest.id, 'accept')"
                >
                  <loading-icon v-if="loadingJoinRequestIds.has(joinRequest.id)" />
                  Accept
                </ui-button>
                <ui-button
                  variant="secondary"
                  size="sm"
                  :disabled="loadingJoinRequestIds.has(joinRequest.id)"
                  @click="reviewJoinRequest(joinRequest.id, 'decline')"
                >
                  Decline
                </ui-button>
              </div>
            </div>
          </template>
        </ui-card>

        <p v-if="filteredPendingJoinRequests?.length === 0" class="text-muted">
          No pending join requests.
        </p>
      </div>
    </ui-skeleton-loader>
  </ui-card>
</template>

<script setup lang="ts">
import {
  useAcceptTeamInvitation,
  useDeclineTeamInvitation,
  useListTeamJoinRequestsByTeam,
} from '@/api/teams/teams'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import { useNotification } from '@/composables/useNotification'
import { computed, ref } from 'vue'

interface Props {
  teamId: number
  searchFilter?: string
  isCaptain?: boolean
}

const props = defineProps<Props>()
const { showNotification } = useNotification()
const { data: joinRequest, isLoading, isLoadingError } = useListTeamJoinRequestsByTeam(props.teamId)

const matches = (parts: (string | undefined)[]) => {
  const q = props.searchFilter?.trim().toLowerCase()
  if (!q) return true
  return parts.some((p) => p?.toLowerCase().includes(q))
}

const filteredPendingJoinRequests = computed(() =>
  joinRequest.value
    ?.filter((r) => r.status === 'pending')
    .filter((r) => matches([r.user.username, r.user.email, r.user.full_name])),
)

const loadingJoinRequestIds = ref<Set<number>>(new Set())
const { mutate: accept } = useAcceptTeamInvitation()
const { mutate: decline } = useDeclineTeamInvitation()

const reviewJoinRequest = (id: number, action: 'accept' | 'decline') => {
  loadingJoinRequestIds.value.add(id)

  const mutate = action === 'accept' ? accept : decline

  mutate(
    { invitationId: id },
    {
      onSuccess: () => {
        const pastTense = { accept: 'accepted', decline: 'declined' }
        showNotification(`Join request ${pastTense[action]}`, 'success')
      },
      onError: (error) => {
        showNotification(error.message, 'error')
      },
      onSettled: () => {
        loadingJoinRequestIds.value.delete(id)
      },
    },
  )
}
</script>

<style scoped>
.join-requests-section {
  display: grid;
  gap: 0.65rem;
}

.join-requests-subhead {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.8rem;
}

.join-requests-subhead h3 {
  margin: 0;
  font-size: 1rem;
}

.join-requests-list {
  overflow-y: auto;
  max-height: 300px;
  display: grid;
  gap: 0.55rem;
  grid-template-rows: auto;
}

.card-item {
  background-color: var(--muted);
}

.join-request-name,
.join-request-email {
  margin: 0;
}

.join-request-user {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.join-request-name {
  font-weight: 700;
}

.join-request-email {
  font-size: 0.84rem;
}

.row-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
</style>
