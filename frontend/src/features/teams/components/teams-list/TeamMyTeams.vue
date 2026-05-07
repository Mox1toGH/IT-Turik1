<template>
  <ui-card :isError="isLoadingError">
    <template #error>
      <div style="display: flex; height: 136px; justify-content: center; align-items: center">
        <p>Error while fetching my teams (code: {{ error?.code }})</p>
      </div>
    </template>

    <template #header>
      <div class="section-head">
        <h2>My teams</h2>
        <ui-skeleton-loader :loading="isLoadingTeams">
          <template #skeleton>
            <ui-skeleton variant="rect" width="70px" />
          </template>

          <span class="text-muted">{{ myTeams?.length ?? 0 }} joined</span>
        </ui-skeleton-loader>
      </div>
    </template>

    <ui-skeleton-loader :loading="isLoadingTeams">
      <template #skeleton>
        <div class="team-grid">
          <ui-card class="team-item" v-for="i in 2" :key="i">
            <template #header>
              <div class="team-header">
                <ui-skeleton variant="rect" width="100%" />
                <ui-skeleton variant="rect" width="160px" />
              </div>
            </template>

            <div style="display: flex; flex-direction: column; gap: 5px">
              <ui-skeleton variant="rect" width="80px" />
              <ui-skeleton variant="rect" width="120px" />
              <ui-skeleton variant="rect" width="100px" />
            </div>

            <template #footer>
              <ui-skeleton variant="rect" height="2rem" width="100%" />
            </template>
          </ui-card>
        </div>
      </template>

      <p v-if="myTeams?.length === 0" class="text-muted">You are not a member of any team yet.</p>

      <div v-else class="team-grid">
        <ui-card v-for="team in myTeamsPageItems" :key="`my-${team.id}`" class="team-item">
          <template #header>
            <div class="team-header">
              <h3 :title="team.name">{{ truncateText(team.name, 15) }}</h3>
              <div class="badges">
                <ui-badge v-if="isCaptain(team)" variant="green">Captain</ui-badge>
                <ui-badge v-if="team.is_in_active_tournament" variant="orange"
                  >Active tournament</ui-badge
                >
              </div>
            </div>
          </template>

          <div>
            <p class="text-muted">Visibility: {{ team.is_public ? 'Public' : 'Private' }}</p>
            <p class="text-muted">Captain: {{ captainName(team) }}</p>
            <p class="text-muted">Members: {{ team.members.length }}</p>
          </div>

          <template #footer>
            <ui-button asLink variant="secondary" size="sm" :to="`/teams/${team.id}`"
              >Open workspace</ui-button
            >
          </template>
        </ui-card>
      </div>
    </ui-skeleton-loader>

    <div v-if="myPages > 1" class="pagination">
      <ui-button size="sm" variant="secondary" :disabled="myPage === 1" @click="myPage -= 1">
        Prev
      </ui-button>
      <span>Page {{ myPage }} / {{ myPages }}</span>
      <ui-button size="sm" variant="secondary" :disabled="myPage === myPages" @click="myPage += 1">
        Next
      </ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import type { GetTeamsResponse } from '@/api/services/teams/types'
import { computed, ref } from 'vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { useTeams } from '@/api/queries/teams'
import { useProfile } from '@/api/queries/accounts'
import { parseApiError } from '@/api/errors'
import { truncateText } from '@/lib/utils'

const TEAMS_PER_PAGE = 8

const { data: user } = useProfile()
const { data: teams, isLoading: isLoadingTeams, isLoadingError, error: teamsError } = useTeams()
const error = computed(() => parseApiError(teamsError.value))

const myTeams = computed(() => teams.value?.filter((team) => isAcceptedMember(team)))
const myTeamsPageItems = computed(() => {
  const from = (myPage.value - 1) * TEAMS_PER_PAGE
  return myTeams.value?.slice(from, from + TEAMS_PER_PAGE)
})

const myPage = ref(1)
const myPages = computed(() =>
  Math.max(1, Math.ceil((myTeams.value?.length ?? 0) / TEAMS_PER_PAGE)),
)

const isCaptain = (team: GetTeamsResponse[number]) => team.captain_id === user.value?.id
const captainName = (team: GetTeamsResponse[number]) => {
  const captain = team.members.find((member) => member.id === team.captain_id)
  return captain?.username || `User #${team.captain_id}`
}
const isAcceptedMember = (team: GetTeamsResponse[number]) => team.is_member || isCaptain(team)
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

.team-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.team-header h3 {
  font-family: var(--font-display);
}

.badges {
  display: flex;
  gap: 0.5rem;
}

.pagination {
  margin-top: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
</style>
