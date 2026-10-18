<template>
  <div :class="['teams-list-wrap', { 'disqualified-wrap': sectionType === 'disqualified' }]">
    <div class="team-label">
      <p class="section-label">{{ sectionTitle }}</p>

      <ui-skeleton-loader :loading="loading">
        <template #skeleton>
          <ui-skeleton variant="rect" width="60px" />
        </template>

        <p class="text-muted">{{ teamCountLabel }}</p>
      </ui-skeleton-loader>
    </div>

    <div class="teams-list">
      <ui-skeleton-loader :loading="loading">
        <template #skeleton>
          <div style="display: flex; flex-direction: column; gap: 0.4rem">
            <ui-skeleton v-for="i in 4" :key="i" variant="rect" height="44px" width="100%" />
          </div>
        </template>

        <template v-if="filteredTeams.length">
          <template v-for="team in filteredTeams" :key="team.id">
            <div class="team-row">
              <slot :team="team" />
            </div>
          </template>
        </template>

        <div v-else class="no-results">
          <p class="no-results-text">No teams match your search</p>
          <button type="button" class="clear-search-btn" @click="$emit('clear-search')">
            Clear search
          </button>
        </div>
      </ui-skeleton-loader>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import type { TournamentTeamResponse } from '@/api/backendAPINinja.schemas'

type Team = TournamentTeamResponse

interface Props {
  sectionType: 'active' | 'disqualified'
  teams?: Team[]
  loading: boolean
  search: string
}

const props = defineProps<Props>()
const emit = defineEmits<{ (e: 'clear-search'): void }>()

const sectionTitle = computed(() =>
  props.sectionType === 'active' ? 'Team' : 'Disqualified Teams',
)

const normalizedSearch = computed(() => props.search.trim().toLowerCase())

const filteredTeams = computed(() => {
  if (!props.teams) return []

  const teams =
    props.sectionType === 'active'
      ? props.teams.filter((team) => !team.is_disqualified)
      : props.teams

  if (!normalizedSearch.value) return teams

  return teams.filter((team) => team.name.toLowerCase().includes(normalizedSearch.value))
})

const teamCountLabel = computed(
  () => `${filteredTeams.value.length} team${filteredTeams.value.length === 1 ? '' : 's'}`,
)
</script>

<style scoped>
.team-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border);
}

.section-label {
  margin: 0;
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted-foreground);
}

.teams-list {
  overflow-y: auto;
  max-height: 320px;
  padding-right: 0.25rem;
}

.disqualified-wrap {
  margin-top: 1.25rem;
}

.team-row {
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
  transition: background-color 0.15s ease;
}

.team-row:last-child {
  border-bottom: 0;
}

.team-row:hover {
  background-color: var(--subtle);
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem 1rem;
  text-align: center;
}

.no-results-text {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--muted-foreground);
}

.clear-search-btn {
  padding: 0.25rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.clear-search-btn:hover {
  background-color: var(--subtle);
}
</style>
