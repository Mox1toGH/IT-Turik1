<template>
  <ui-card title="Join Requests">
    <ui-query-block :query="joinRequestsQuery">
      <template #error>
        <div style="display: flex; justify-content: center; align-items: center; height: 200px">
          <p>Failed to fetch join requests</p>
        </div>
      </template>

      <ui-query-field>
        <template #skeleton>
          <div class="join-requests-section">
            <div class="join-requests-list">
              <div v-for="i in 2" :key="i" class="join-request-card">
                <div class="join-request-user">
                  <ui-skeleton variant="rounded" width="44px" height="44px" />
                  <div class="join-request-main">
                    <ui-skeleton variant="rect" width="150px" />
                    <ui-skeleton variant="rect" width="190px" />
                  </div>
                </div>
                <div class="row-actions">
                  <ui-skeleton variant="rect" height="34px" width="82px" />
                  <ui-skeleton variant="rect" height="34px" width="82px" />
                </div>
              </div>
            </div>
          </div>
        </template>

        <template #default>
          <p v-if="isEmpty" class="text-muted">No pending join requests.</p>
          <div v-else class="join-requests-list">
            <article
              class="join-request-card"
              v-for="joinRequest in filteredPendingJoinRequests"
              :key="`join-request-${joinRequest.id}`"
            >
              <div class="join-request-user">
                <user-avatar
                  :avatar="joinRequest.user.avatar"
                  :username="joinRequest.user.username"
                  :full-name="joinRequest.user.full_name"
                  :size="44"
                />
                <div class="join-request-main">
                  <p class="join-request-name">
                    {{ joinRequest.user.full_name || joinRequest.user.username }}
                  </p>
                  <p v-if="joinRequest.user.full_name" class="join-request-username">
                    @{{ joinRequest.user.username }}
                  </p>
                  <p class="text-muted join-request-email">{{ joinRequest.user.email }}</p>
                </div>
              </div>

              <div class="row-actions">
                <ui-button
                  size="sm"
                  :disabled="loadingJoinRequestIds.has(joinRequest.id)"
                  @click="reviewJoinRequest(joinRequest.id, 'accept')"
                >
                  <LoaderCircle
                    class="animate-spin"
                    v-if="loadingJoinRequestIds.has(joinRequest.id)"
                  />
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
            </article>
          </div>
        </template>
      </ui-query-field>
    </ui-query-block>
  </ui-card>
</template>

<script setup lang="ts">
import {
  useAcceptTeamJoinRequest,
  useDeclineTeamJoinRequest,
  useListTeamJoinRequestsByTeam,
} from '@/api/teams/teams'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import { getListTeamMembersQueryKey } from '@/api/teams/teams'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import { useNotification } from '@/composables/useNotification'
import { LoaderCircle } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'

interface Props {
  teamId: number
  searchFilter?: string
  isCaptain?: boolean
}

const props = defineProps<Props>()
const queryClient = useQueryClient()
const { showNotification } = useNotification()
const joinRequestsQuery = useListTeamJoinRequestsByTeam(props.teamId)
const { data: joinRequest } = joinRequestsQuery

const matches = (parts: (string | undefined)[]) => {
  const q = props.searchFilter?.trim().toLowerCase()
  if (!q) return true
  return parts.some((p) => p?.toLowerCase().includes(q))
}

const filteredPendingJoinRequests = computed(() =>
  (joinRequest.value?.items ?? [])
    ?.filter((r) => r.status === 'pending')
    .filter((r) => matches([r.user.username, r.user.email, r.user.full_name])),
)

const isEmpty = computed(() => filteredPendingJoinRequests.value.length === 0)

const loadingJoinRequestIds = ref<Set<number>>(new Set())
const { mutate: accept } = useAcceptTeamJoinRequest()
const { mutate: decline } = useDeclineTeamJoinRequest()

const reviewJoinRequest = (id: number, action: 'accept' | 'decline') => {
  loadingJoinRequestIds.value.add(id)

  const mutate = action === 'accept' ? accept : decline

  mutate(
    { pk: props.teamId, requestId: id },
    {
      onSuccess: () => {
        void queryClient.invalidateQueries({
          queryKey: getListTeamMembersQueryKey(props.teamId),
        })
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

.join-requests-list {
  overflow-y: auto;
  max-height: 300px;
  display: grid;
  gap: 0.75rem;
  padding: 1px;
}

.join-request-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--background);
  transition:
    border-color 0.18s ease,
    background-color 0.18s ease;
}

.join-request-card:hover {
  border-color: var(--primary);
  background: var(--muted);
}

.join-request-name,
.join-request-email {
  margin: 0;
}

.join-request-user {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  min-width: 0;
}

.join-request-main {
  display: grid;
  gap: 0.15rem;
  min-width: 0;
}

.join-request-name {
  font-weight: 700;
  overflow-wrap: anywhere;
}

.join-request-username {
  margin: 0;
  color: var(--muted-foreground);
  font-size: 0.82rem;
}

.join-request-email {
  font-size: 0.84rem;
  overflow-wrap: anywhere;
}

.row-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

@media (max-width: 620px) {
  .join-request-card {
    grid-template-columns: minmax(0, 1fr);
  }

  .row-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (prefers-reduced-motion: reduce) {
  .join-request-card {
    transition: none;
  }
}
</style>
