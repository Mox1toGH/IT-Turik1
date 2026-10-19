<template>
  <ui-section title="Rounds Timeline" description="Schedule and criteria per round">
    <div v-if="rounds.length" class="rounds-list">
      <ui-card v-for="round in rounds" :key="round.id" class="round-card">
        <p class="round-title">{{ round.name }}</p>
        <p class="round-meta">{{ formatDateRange(round.start_date, round.end_date) }}</p>
        <p class="round-meta">Start: {{ formatArchiveDateTime(round.start_date) }}</p>
        <p class="round-meta">End: {{ formatArchiveDateTime(round.end_date) }}</p>
        <p class="round-meta">Criteria: {{ round.criteria?.length ?? 0 }}</p>
      </ui-card>
    </div>
    <p v-else class="empty-state">No rounds found.</p>
  </ui-section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiSection from '@/components/ui/UiSection'
import { formatArchiveDateTime, formatDateRange } from './lib/format'
import type { TournamentArchive } from '@/features/tournaments/types'

defineProps<{
  rounds: NonNullable<TournamentArchive['rounds']>
}>()
</script>

<style scoped>
.rounds-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
}

.round-title,
.round-meta {
  margin: 0;
}

.round-title {
  font-weight: 600;
}

.round-meta {
  color: var(--muted-foreground);
}

.empty-state {
  margin: 0;
  color: var(--muted-foreground);
}
</style>
