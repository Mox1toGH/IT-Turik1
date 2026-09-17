<template>
  <ui-card variant="panel" :isError="isLoadingError">
    <template #error>
      <div style="display: flex; height: 136px; justify-content: center; align-items: center">
        <p>Error while fetching my teams (code: {{ teamsError?.code }})</p>
      </div>
    </template>

    <template #header>
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Your workspace</p>
          <h2 class="text-3xl">My teams</h2>
          <p class="section-subtitle text-base">Teams where you are a member or captain.</p>
        </div>

        <div class="section-meta">
          <ui-skeleton-loader :loading="isLoadingTeams">
            <template #skeleton>
              <ui-skeleton variant="rect" width="82px" height="38px" />
            </template>

            <span class="count-pill text-base">{{ myTeams?.length ?? 0 }} joined</span>
          </ui-skeleton-loader>
        </div>
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

      <div v-if="myTeams?.length === 0" class="empty-row">
        <div class="empty-icon" aria-hidden="true">+</div>
        <div class="empty-copy">
          <h3 class="text-lg">No joined teams</h3>
          <p class="text-base">Create a team or request to join an available workspace.</p>
        </div>
      </div>

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
            <ui-button asLink variant="default" size="sm" :to="`/teams/${team.id}`"
              >Open workspace</ui-button
            >
          </template>
        </ui-card>
      </div>
    </ui-skeleton-loader>

    <ui-pagination
      v-if="myPages > 1"
      v-model="myPage"
      :total-items="myTeams?.length ?? 0"
      :page-size="TEAMS_PER_PAGE"
      :show-summary="false"
    />
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiPagination from '@/components/ui/UiPagination.vue'
import { computed, ref } from 'vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { truncateText } from '@/lib/utils'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useListTeams, type ListTeamsQueryResult } from '@/api/teams/teams'

const TEAMS_PER_PAGE = 8

type Team = ListTeamsQueryResult[number]

const { data: user } = useGetUserProfile()
const { data: teams, isLoading: isLoadingTeams, isLoadingError, error: teamsError } = useListTeams()

const myTeams = computed(() => teams.value?.filter((team) => isAcceptedMember(team)))
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

.team-header {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem;
}

.team-header h3 {
  font-family: var(--font-display);
  min-width: 0;
}

.badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.5rem;
  max-width: 100%;
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
}
</style>
