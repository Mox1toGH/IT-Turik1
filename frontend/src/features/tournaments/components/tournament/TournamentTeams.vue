<template>
  <ui-card class="tournament-card" :is-error="isError">
    <template #header>
      <h2 class="tournament-card-title">Teams Info</h2>
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

      <div class="team-label">
        <p>Team</p>

        <ui-skeleton-loader :loading="isTeamsLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="60px" />
          </template>

          <p class="text-muted">
            {{ filteredTeams.length }} team{{ filteredTeams.length === 1 ? '' : 's' }}
          </p>
        </ui-skeleton-loader>
      </div>

      <div class="teams-list">
        <ui-skeleton-loader :loading="isTeamsLoading">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 0.4rem">
              <ui-skeleton v-for="i in 4" :key="i" variant="rect" height="48px" width="100%" />
            </div>
          </template>

          <template v-if="filteredTeams.length">
            <RouterLink
              :to="`/teams/${team.id}`"
              v-for="team in filteredTeams"
              :key="team.id"
              class="team-item"
            >
              <div class="team-info">
                <TeamIcon />
                {{ team.name }}
              </div>

              <ui-badge variant="primary"> {{ team.members_count }} members </ui-badge>
            </RouterLink>
          </template>

          <p v-else class="text-muted">No teams found.</p>
        </ui-skeleton-loader>
      </div>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import TeamIcon from '@/icons/TeamIcon.vue'
import { RouterLink } from 'vue-router'
import { parseApiError } from '@/api/errors'
import { useRegisteredTeams } from '@/api/queries/tournaments'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()

const search = ref('')

const {
  data: teams,
  isLoading: isTeamsLoading,
  error: teamsError,
  isError,
} = useRegisteredTeams({ id: props.tournamentId })
const error = computed(() => parseApiError(teamsError.value))

const filteredTeams = computed(() => {
  if (!teams.value) return []

  const term = search.value.trim().toLowerCase()
  if (!term) return teams.value

  return teams.value.filter((team) => team.name.toLowerCase().includes(term))
})
</script>

<style scoped>
.tournament-card {
  flex: 1;
}

.tournament-card-title {
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.team-search {
  width: 100%;
  margin-bottom: 1rem;
}

.team-info {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.team-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  padding: 0.7rem 10px 0.7rem 0;
}

.team-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.teams-list {
  overflow-y: auto;
  max-height: 215px;
}
</style>
