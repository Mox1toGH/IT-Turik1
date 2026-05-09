<template>
  <ui-card :isError="isLoadingError">
    <template #error>
      <div style="display: flex; height: 200px; justify-content: center; align-items: center">
        <p>Error while fetching invitations (code: {{ error?.code }})</p>
      </div>
    </template>

    <template #header>
      <div class="section-head">
        <h2>Other teams</h2>
        <ui-skeleton-loader :loading="isLoadingTeams">
          <template #skeleton>
            <ui-skeleton variant="rect" width="80px" />
          </template>

          <span class="text-muted">{{ otherTeams?.length ?? 0 }} available</span>
        </ui-skeleton-loader>
      </div>
    </template>

    <ui-skeleton-loader :loading="isLoadingTeams">
      <template #skeleton>
        <div class="team-grid">
          <ui-card class="team-item" v-for="i in 2" :key="i">
            <template #header>
              <ui-skeleton variant="rect" width="120px" />
            </template>

            <div style="display: flex; flex-direction: column; gap: 4px">
              <ui-skeleton variant="rect" width="80px" />
              <ui-skeleton variant="rect" width="120px" />
              <ui-skeleton variant="rect" width="100px" />
              <ui-skeleton variant="rect" width="110px" />
            </div>

            <template #footer>
              <div class="actions">
                <ui-skeleton variant="rect" height="2rem" width="100%" />
                <ui-skeleton variant="rect" height="2rem" width="100%" />
              </div>
            </template>
          </ui-card>
        </div>
      </template>

      <p v-if="otherTeams?.length === 0" class="text-muted">No other teams available.</p>
      <div v-else class="team-grid">
        <ui-card v-for="team in otherTeamsPageItems" :key="`other-${team.id}`" class="team-item">
          <template #header>
            <div class="team-meta">
              <h3 :title="team.name">{{ truncateText(team.name, 60) }}</h3>
            </div>
          </template>

          <div>
            <p class="text-muted">Visibility: {{ team.is_public ? 'Public' : 'Private' }}</p>
            <p class="text-muted">Captain: {{ captainName(team) }}</p>
            <p class="text-muted">Members: {{ team.members.length }}</p>
          </div>

          <template #footer>
            <div class="actions">
              <ui-button
                size="sm"
                variant="secondary"
                v-if="team.can_request_to_join"
                style="width: 100%"
                :disabled="loadingIds.has(team.id)"
                @click="sendJoinRequest(team.id)"
              >
                <loading-icon v-if="loadingIds.has(team.id)" />
                Request to join
              </ui-button>
              <ui-button asLink variant="secondary" size="sm" :to="`/teams/${team.id}`"
                >Open workspace</ui-button
              >
            </div>
          </template>
        </ui-card>
      </div>
    </ui-skeleton-loader>

    <div v-if="otherPages > 1" class="pagination">
      <ui-button
        size="sm"
        variant="secondary"
        class="btn-soft"
        :disabled="otherPage === 1"
        @click="otherPage -= 1"
        type="button"
      >
        Prev
      </ui-button>
      <span>Page {{ otherPage }} / {{ otherPages }}</span>
      <ui-button
        size="sm"
        variant="secondary"
        :disabled="otherPage === otherPages"
        @click="otherPage += 1"
        type="button"
      >
        Next
      </ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useNotification } from '@/composables/useNotification'
import type { TeamId } from '@/api/dbTypes'
import type { GetTeamInfoResponse } from '@/api/services/teams/types'
import { computed, ref } from 'vue'
import { useSendJoinRequest, useTeams } from '@/api/queries/teams'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { useProfile } from '@/api/queries/accounts'
import { parseApiError } from '@/api/errors'
import { truncateText } from '@/lib/utils'

const OTHER_TEAMS_PER_PAGE = 8

const { data: user } = useProfile()
const { data: teams, isLoading: isLoadingTeams, isLoadingError, error: teamsError } = useTeams()
const error = computed(() => parseApiError(teamsError.value))

const { showNotification } = useNotification()

const otherPage = ref(1)
const loadingIds = ref<Set<TeamId>>(new Set())

const isCaptain = (team: GetTeamInfoResponse) => team.captain_id === user.value?.id
const captainName = (team: GetTeamInfoResponse) => {
  const captain = team.members.find((member) => member.id === team.captain_id)
  return captain?.username || `User #${team.captain_id}`
}
const isAcceptedMember = (team: GetTeamInfoResponse) => team.is_member || isCaptain(team)

const otherTeams = computed(() => teams.value?.filter((team) => !isAcceptedMember(team)))
const otherPages = computed(() =>
  Math.max(1, Math.ceil((otherTeams.value?.length ?? 0) / OTHER_TEAMS_PER_PAGE)),
)
const otherTeamsPageItems = computed(() => {
  const from = (otherPage.value - 1) * OTHER_TEAMS_PER_PAGE
  return otherTeams.value?.slice(from, from + OTHER_TEAMS_PER_PAGE)
})

const { mutate: sendJoinRequestMutate } = useSendJoinRequest()

const sendJoinRequest = (teamId: TeamId) => {
  loadingIds.value.add(teamId)
  sendJoinRequestMutate(
    { id: teamId },
    {
      onSuccess: () => {
        showNotification('Join request sent.', 'success')
      },
      onError: (err) => {
        showNotification(
          err.response ? 'Unable to send join request.' : 'Unable to connect to server.',
          'error',
        )
      },
      onSettled: () => {
        loadingIds.value.delete(teamId)
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

.pagination {
  margin-top: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
</style>
