<template>
  <ui-card variant="panel" class="tournament-card" :is-error="isError">
    <template #header>
      <div class="tournament-card-head">
        <div>
          <p class="section-eyebrow">Teams</p>
          <h2 class="text-3xl">Teams info</h2>
          <p class="section-subtitle text-base">Registered and disqualified teams.</p>
        </div>

        <span class="count-pill text-base">{{ activeTeams?.length ?? 0 }} active</span>
      </div>
    </template>

    <template #error>
      <div style="display: flex; height: 300px; justify-content: center; align-items: center">
        <p>Error while fetching tournament teams (code: {{ error?.code }})</p>
      </div>
    </template>

    <div>
      <ui-input
        v-model="search"
        placeholder="Search team"
        class="team-search"
        :disabled="isTeamsLoading"
      />

      <TournamentTeamSection
        sectionType="active"
        :teams="activeTeams"
        :loading="isActiveTeamsLoading"
        :search="search"
      >
        <template #default="{ team }">
          <TeamCard :team="team" :tournament="tournament" :is-admin="isAdmin" />
        </template>
      </TournamentTeamSection>

      <TournamentTeamSection
        v-if="hasDisqualifiedTeams"
        sectionType="disqualified"
        :teams="teams"
        :loading="isTeamsLoading"
        :search="search"
      >
        <template #default="{ team }">
          <TeamCard :team="team" :tournament="tournament" :is-admin="isAdmin" is-disqualified />
        </template>
      </TournamentTeamSection>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import TournamentTeamSection from './tournament-teams/TournamentTeamSection.vue'
import { useGetTournament, useListTournamentTeams } from '@/api/tournaments/tournaments'
import { useGetUserProfile } from '@/api/accounts/accounts'
import TeamCard from './TeamCard.vue'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const search = ref('')

const { data: tournament } = useGetTournament(props.tournamentId)
const {
  data: activeTeams,
  isLoading: isActiveTeamsLoading,
  error: activeTeamsError,
  isError: isActiveTeamsError,
} = useListTournamentTeams(props.tournamentId, { status: 'all' })
const {
  data: teams,
  isLoading: isTeamsLoading,
  error: disqualifiedTeamsError,
  isError: isDisqualifiedTeamsError,
} = useListTournamentTeams(props.tournamentId, { status: 'disqualified' })
const isError = computed(() => isActiveTeamsError.value || isDisqualifiedTeamsError.value)
const error = computed(() => activeTeamsError.value || disqualifiedTeamsError.value)

const hasDisqualifiedTeams = computed(() => (teams.value?.length ?? 0) > 0)
const { data: user } = useGetUserProfile()
const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.role === 'organizer')
</script>

<style scoped>
.tournament-card {
  flex: 1;
}

.tournament-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.tournament-card-head h2 {
  margin: 2rem 0 0.45rem;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.tournament-card-head .section-subtitle {
  margin: 0;
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

.team-search {
  width: 100%;
  margin-bottom: 0.9rem;
}

.teams-list-wrap {
  background-color: var(--muted);
}

.teams-list {
  overflow-y: auto;
  max-height: 400px;
}

.disqualified-wrap {
  margin-top: 1rem;
}

.label-with-icon {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.team-row {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--border);
}

@media (max-width: 700px) {
  .tournament-card-head,
  .team-item {
    align-items: flex-start;
    flex-direction: column;
  }

  .team-action-group {
    flex-wrap: wrap;
  }
}
</style>
