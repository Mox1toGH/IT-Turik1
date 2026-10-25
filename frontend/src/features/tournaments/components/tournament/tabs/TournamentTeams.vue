<template>
  <ui-card class="teams-card">
    <template #header>
      <div class="teams-header">
        <div class="teams-header-text">
          <p class="section-eyebrow">Teams</p>
          <h2 class="text-2xl">Teams info</h2>
          <p class="section-subtitle text-base">Registered and disqualified teams.</p>
        </div>
        <span class="count-pill">{{ activeTeams.length }} active</span>
      </div>
    </template>

    <div class="teams-body">
      <div class="teams-search-wrap">
        <SearchIcon class="search-icon" />
        <ui-input
          v-model="search"
          placeholder="Search teams..."
          class="team-search"
          :disabled="isActiveTeamsLoading"
        />
      </div>

      <ui-query-block :query="activeTeamsQuery">
        <ui-query-field>
          <template #skeleton>
            <div class="skeleton-stack">
              <ui-skeleton variant="rect" height="40px" width="100%" />
              <ui-skeleton v-for="i in 4" :key="i" variant="rect" height="44px" width="100%" />
            </div>
          </template>
          <ui-empty-card
            v-if="
              !isDisqualifiedTeamsLoading &&
              activeTeams.length === 0 &&
              disqualifiedTeams.length === 0
            "
            message="No teams registered yet."
          />

          <TournamentTeamSection
            v-if="activeTeams.length"
            sectionType="active"
            :teams="activeTeams"
            :search="search"
            @clear-search="search = ''"
          >
            <template #default="{ team }">
              <TeamCard :team="team" :tournament="tournament" :is-admin="isAdmin" />
            </template>
          </TournamentTeamSection>

          <TournamentTeamSection
            v-if="hasDisqualifiedTeams"
            sectionType="disqualified"
            :teams="disqualifiedTeams"
            :search="search"
            @clear-search="search = ''"
          >
            <template #default="{ team }">
              <TeamCard :team="team" :tournament="tournament" :is-admin="isAdmin" is-disqualified />
            </template>
          </TournamentTeamSection>
        </ui-query-field>
      </ui-query-block>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiCard from '@/components/ui/UiCard'
import UiEmptyCard from '@/components/ui/UiEmptyCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiInput from '@/components/ui/UiInput'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { SearchIcon } from 'lucide-vue-next'
import TournamentTeamSection from './tournament-teams/TournamentTeamSection.vue'
import { useGetTournament, useListTournamentTeams } from '@/api/tournaments/tournaments'
import { useGetUserProfile } from '@/api/accounts/accounts'
import TeamCard from '../TeamCard.vue'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const search = ref('')

const { data: tournament } = useGetTournament(props.tournamentId)
// Primary query: drives the section's status. 'active' filters is_active=True on the
// backend ('all' would also return disqualified and inactive registrations).
const activeTeamsQuery = useListTournamentTeams(props.tournamentId, { status: 'active' })
// Secondary query: own loading state, never affects the section's status.
const disqualifiedTeamsQuery = useListTournamentTeams(props.tournamentId, {
  status: 'disqualified',
})
const { data: activeTeamsData, isLoading: isActiveTeamsLoading } = activeTeamsQuery
const { data: disqualifiedTeamsData, isLoading: isDisqualifiedTeamsLoading } =
  disqualifiedTeamsQuery
const activeTeams = computed(() => activeTeamsData.value?.items ?? [])
const disqualifiedTeams = computed(() => disqualifiedTeamsData.value?.items ?? [])

const hasDisqualifiedTeams = computed(() => disqualifiedTeams.value.length > 0)
const { data: user } = useGetUserProfile()
const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.role === 'organizer')
</script>

<style scoped>
.teams-card {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.teams-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.teams-header-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.teams-header-text h2 {
  margin: 0.25rem 0 0.25rem;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.teams-header-text .section-subtitle {
  margin: 0;
}

.section-eyebrow {
  margin: 0;
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted-foreground);
}

.count-pill {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--muted-foreground);
  white-space: nowrap;
  font-size: var(--text-sm);
  flex-shrink: 0;
}

.teams-body {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
  gap: 0;
}

.teams-search-wrap {
  position: relative;
  padding: 1.25rem 0;
  border-bottom: 1px solid var(--border);
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--muted-foreground);
  pointer-events: none;
  z-index: 1;
}

.team-search {
  width: 100%;
  padding-left: 2.25rem;
}

.skeleton-stack {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

@media (max-width: 700px) {
  .teams-header {
    flex-direction: column;
  }
}
</style>
