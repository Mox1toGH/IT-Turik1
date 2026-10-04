<template>
  <ui-card class="section-block">
    <template #header>
      <div class="section-head">
        <h2>Participating Teams</h2>
        <p class="section-note">Teams registered in this archive</p>
      </div>
    </template>
    <div v-if="teams.length" class="team-grid">
      <ui-card v-for="team in teams" :key="team.id" class="team-chip">{{ team.name }}</ui-card>
    </div>
    <ui-card v-else>
      <p class="empty-state">No participating teams found.</p>
    </ui-card>
  </ui-card>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import type { TournamentArchiveDetailResponse } from '@/api/backendAPINinja.schemas'

defineProps<{
  teams: NonNullable<TournamentArchiveDetailResponse['teams']>
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

.team-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.team-chip {
  text-align: center;
  font-weight: 600;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--muted) 78%, transparent),
    color-mix(in srgb, var(--background) 88%, transparent)
  ) !important;
  border: 1px solid color-mix(in srgb, var(--line-soft) 70%, transparent);
}

.empty-state {
  margin: 0;
  color: var(--muted-foreground);
}

@media (max-width: 980px) {
  .team-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .section-note {
    width: 100%;
  }
}
</style>
