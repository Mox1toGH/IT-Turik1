<template>
  <ui-section title="Participating Teams" description="Teams registered in this archive">
    <div v-if="teams.length" class="team-grid">
      <span v-for="team in teams" :key="team.id" class="team-chip">{{ team.name }}</span>
    </div>
    <ui-empty-card v-else message="No participating teams found." />
  </ui-section>
</template>

<script setup lang="ts">
import UiSection from '@/components/ui/UiSection'
import UiEmptyCard from '@/components/ui/UiEmptyCard'
import type { TournamentArchiveDetailResponse } from '@/api/backendAPINinja.schemas'

defineProps<{
  teams: NonNullable<TournamentArchiveDetailResponse['teams']>
}>()
</script>

<style scoped>
.team-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.team-chip {
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  background: var(--subtle);
  color: var(--foreground);
  font-weight: 600;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  overflow-wrap: anywhere;
}

</style>
