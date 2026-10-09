<template>
  <ui-card class="section-block">
    <template #header>
      <div class="section-head">
        <h2>Rounds Timeline</h2>
        <p class="section-note">Schedule and criteria per round</p>
      </div>
    </template>
    <div v-if="rounds.length" class="rounds-list">
      <ui-card v-for="round in rounds" :key="round.id" class="round-card">
        <p class="round-title">{{ round.name }}</p>
        <p class="round-meta">{{ formatDateRange(round.start_date, round.end_date) }}</p>
        <p class="round-meta">Start: {{ formatArchiveDateTime(round.start_date) }}</p>
        <p class="round-meta">End: {{ formatArchiveDateTime(round.end_date) }}</p>
        <p class="round-meta">Criteria: {{ round.criteria?.length ?? 0 }}</p>
      </ui-card>
    </div>
    <ui-card v-else>
      <p class="empty-state">No rounds found.</p>
    </ui-card>
  </ui-card>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import { formatArchiveDateTime, formatDateRange } from './lib/format'
import type { TournamentArchiveDetailResponse } from '@/api/backendAPINinja.schemas'

defineProps<{
  rounds: NonNullable<TournamentArchiveDetailResponse['rounds']>
}>()
</script>

<style scoped>
.section-block {
  display: grid;
  gap: 0.6rem;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.section-block h2 {
  margin: 0;
}

.section-note {
  margin: 0;
  color: var(--muted-foreground);
  font-size: 0.88rem;
}

.rounds-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.round-card {
  border: 1px solid color-mix(in srgb, var(--line-soft) 75%, transparent);
  background: linear-gradient(
    180deg,
    var(--card-background, transparent),
    color-mix(in srgb, var(--muted) 35%, transparent)
  );
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

@media (max-width: 980px) {
  .rounds-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .section-note {
    width: 100%;
  }
}
</style>
