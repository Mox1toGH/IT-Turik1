<template>
  <ui-section
    title="Teams info"
    description="Registered and disqualified teams."
  >
    <template #actions>
      <span class="count-pill text-base">{{ activeTeams?.length ?? 0 }} active</span>
    </template>

    <div
      v-if="status === 'error'"
      style="display: flex; height: 300px; justify-content: center; align-items: center"
    >
      <p>Error while fetching tournament teams</p>
    </div>

    <ui-skeleton-loader v-else-if="status === 'loading'" :loading="true">
      <template #skeleton>
        <div style="display: flex; flex-direction: column; gap: 0.4rem">
          <ui-skeleton v-for="i in 4" :key="i" variant="rect" height="48px" width="100%" />
        </div>
      </template>
    </ui-skeleton-loader>

    <p v-else-if="status === 'empty'" class="card-muted">No teams registered yet</p>

    <div v-else>
      <ui-input
        v-model="search"
        placeholder="Search team"
        class="team-search"
        :disabled="isActiveTeamsLoading"
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
        :teams="disqualifiedTeams"
        :loading="isDisqualifiedTeamsLoading"
        :search="search"
      >
        <template #default="{ team }">
          <TeamCard :team="team" :tournament="tournament" :is-admin="isAdmin" is-disqualified />
        </template>
      </TournamentTeamSection>
    </div>
  </ui-section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiInput from '@/components/ui/UiInput'
import UiSection from '@/components/ui/UiSection'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import TournamentTeamSection from './tournament-teams/TournamentTeamSection.vue'
import { useGetTournament, useListTournamentTeams } from '@/api/tournaments/tournaments'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useCardState } from '@/composables/useCardState'
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
const { data: activeTeams, isLoading: isActiveTeamsLoading } = activeTeamsQuery
const { data: disqualifiedTeams, isLoading: isDisqualifiedTeamsLoading } = disqualifiedTeamsQuery
const { status } = useCardState(activeTeamsQuery)

const hasDisqualifiedTeams = computed(() => (disqualifiedTeams.value?.length ?? 0) > 0)
const { data: user } = useGetUserProfile()
const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.role === 'organizer')
</script>

<style scoped>
.count-pill {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--muted-foreground);
  white-space: nowrap;
}

.team-search {
  width: 100%;
  margin-bottom: 0.9rem;
}

.card-muted {
  margin: 0;
  font-size: 0.9rem;
  color: var(--muted-foreground);
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
  .team-item {
    align-items: flex-start;
    flex-direction: column;
  }

  .team-action-group {
    flex-wrap: wrap;
  }
}
</style>
