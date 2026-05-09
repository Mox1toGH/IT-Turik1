<template>
  <ui-card :class="['teams-list-wrap', { 'disqualified-wrap': sectionType === 'disqualified' }]">
    <div class="team-label">
      <p>{{ sectionTitle }}</p>

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
            <ui-skeleton v-for="i in 4" :key="i" variant="rect" height="48px" width="100%" />
          </div>
        </template>

        <template v-if="filteredTeams.length">
          <template v-for="team in filteredTeams" :key="team.id">
            <div class="team-row">
              <slot :team="team" />
            </div>
          </template>
        </template>

        <p v-else class="text-muted">No teams found.</p>
      </ui-skeleton-loader>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import type { GetRegisteredTeamsResponse } from '@/api/services/tournaments/types'

type Team = GetRegisteredTeamsResponse[number]

interface Props {
  sectionType: 'active' | 'disqualified'
  teams?: Team[]
  loading: boolean
  search: string
}

const props = defineProps<Props>()

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
  margin-bottom: 1rem;
}

.teams-list {
  overflow-y: auto;
  max-height: 400px;
}

.disqualified-wrap {
  margin-top: 1rem;
}

.team-row {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--border);
}
</style>
