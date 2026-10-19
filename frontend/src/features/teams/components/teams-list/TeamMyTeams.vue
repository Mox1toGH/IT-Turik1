<template>
  <div class="teams-widget">
    <div
      v-if="status === 'error'"
      style="display: flex; height: 136px; justify-content: center; align-items: center"
    >
      <p>Error while fetching my teams</p>
    </div>

    <div v-else class="teams-body">
      <div v-if="isStale" class="stale-banner" role="status">
        <span>Update failed</span>
        <button type="button" :disabled="isFetching" @click="() => refetch()">
          {{ isFetching ? 'Retrying…' : 'Retry' }}
        </button>
      </div>

      <div :class="{ dimmed: isFetching }" :aria-busy="isFetching || undefined">
        <ui-query-state :query="teamsQuery">
<template #skeleton>
            <div class="team-grid">
              <div class="team-item-skeleton" v-for="i in 2" :key="i">
                <div class="team-skeleton-body">
                  <div class="team-header">
                    <ui-skeleton variant="rect" width="100%" />
                    <ui-skeleton variant="rect" width="160px" />
                  </div>

                  <div style="display: flex; flex-direction: column; gap: 5px">
                    <ui-skeleton variant="rect" width="80px" />
                    <ui-skeleton variant="rect" width="120px" />
                    <ui-skeleton variant="rect" width="100px" />
                  </div>

                  <ui-skeleton variant="rect" height="2rem" width="100%" />
                </div>
              </div>
            </div>
          </template><p v-if="myTeams?.length === 0" class="empty-text text-muted">
            No joined teams yet. Create a team or request to join an available workspace.
          </p><div v-else class="team-grid">
            <ui-card v-for="team in myTeamsPageItems" :key="`my-${team.id}`" class="team-item">
              <div class="team-body">
                <div class="team-header">
                  <ui-truncate :text="team.name" class="team-title" />
                  <div class="badges">
                    <ui-badge v-if="isCaptain(team)" variant="green">Captain</ui-badge>
                    <ui-badge v-if="team.is_in_active_tournament" variant="orange"
                      >Active tournament</ui-badge
                    >
                  </div>
                </div>

                <div class="team-details">
                  <p class="text-muted">Visibility: {{ team.is_public ? 'Public' : 'Private' }}</p>
                  <p class="text-muted">Captain: {{ captainName(team) }}</p>
                  <p class="text-muted">Members: {{ team.members.length }}</p>
                </div>
              </div>

              <template #footer>
                <ui-button asLink variant="default" size="sm" :to="`/teams/${team.id}`"
                  >Open workspace</ui-button
                >
              </template>
            </ui-card>
          </div>
</ui-query-state>

        <ui-pagination
          v-if="myPages > 1"
          v-model="myPage"
          :total-items="myTeams?.length ?? 0"
          :page-size="TEAMS_PER_PAGE"
          :show-summary="false"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiPagination from '@/components/ui/UiPagination'
import UiTruncate from '@/components/ui/UiTruncate'
import { computed, ref } from 'vue'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useQueryState } from '@/composables/useQueryState'
import { useListTeams, type ListTeamsQueryResult } from '@/api/teams/teams'

const TEAMS_PER_PAGE = 8

type Team = ListTeamsQueryResult['items'][number]

const { data: user } = useGetUserProfile()
const teamsQuery = useListTeams()
const { data: teams, isLoading: isLoadingTeams, isFetching, refetch } = teamsQuery
const { status, isStale } = useQueryState(teamsQuery)

const myTeams = computed(() =>
  (teams.value?.items ?? []).filter((team) => isAcceptedMember(team)),
)
const myTeamsPageItems = computed(() => {
  const from = (myPage.value - 1) * TEAMS_PER_PAGE
  return myTeams.value?.slice(from, from + TEAMS_PER_PAGE)
})

const myPage = ref(1)
const myPages = computed(() =>
  Math.max(1, Math.ceil((myTeams.value?.length ?? 0) / TEAMS_PER_PAGE)),
)

const isCaptain = (team: Team) => team.captain_id === user.value?.id
const captainName = (team: Team) => {
  const captain = team.members.find((member) => member.id === team.captain_id)
  return captain?.username || `User #${team.captain_id}`
}
const isAcceptedMember = (team: Team) => team.is_member || isCaptain(team)
</script>

<style scoped>
.teams-widget {
  display: grid;
  gap: 1rem;
  min-width: 0;
}

.empty-text {
  margin: 0;
  padding: 2rem 0;
  text-align: center;
  overflow-wrap: anywhere;
}

.teams-body {
  display: grid;
  gap: 1rem;
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

.team-header {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem;
}

.team-header h3,
.team-title {
  font-family: var(--font-display);
  min-width: 0;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 800;
}

.team-details {
  display: grid;
  gap: 0.25rem;
  min-width: 0;
}

.team-details p {
  margin: 0;
  overflow-wrap: anywhere;
}

.team-item :deep(.card-footer) {
  padding: 0 1.25rem 1.25rem;
}

.badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.5rem;
  max-width: 100%;
}

.dimmed > * {
  opacity: 0.6;
}

.stale-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.35rem 0.6rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--subtle);
  color: var(--muted-foreground);
  font-size: 0.8rem;
}

.stale-banner button {
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  font-weight: 600;
  text-decoration: underline;
  cursor: pointer;
}

.stale-banner button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.stale-banner button:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}
</style>
