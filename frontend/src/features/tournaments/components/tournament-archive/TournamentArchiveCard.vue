<template>
  <ui-card class="archive-card">
    <img
      v-if="tournament.banner"
      class="archive-media"
      :src="tournament.banner"
      :alt="`${tournament.name} banner`"
    />

    <div class="archive-body">
      <ui-truncate :text="tournament.name" class="archive-card-title" />

      <p class="archive-description">{{ tournament.description || 'No description provided.' }}</p>

      <div class="archive-meta">
        <div class="archive-date">
          <p>Finished:</p>
          <p>{{ formatDate(tournament.end_date) }}</p>
        </div>
        <p class="archive-count">{{ tournament.standings.length }} standings</p>
      </div>
    </div>

    <template #footer>
      <ui-button
        asLink
        :to="`/tournaments/archive/${tournament.id}`"
        size="sm"
        variant="secondary"
        class="archive-details-btn"
      >
        View archive
      </ui-button>
    </template>
  </ui-card>
</template>

<script setup lang="ts">
import type { TournamentArchive } from '@/features/tournaments/types'
import UiCard from '@/components/ui/UiCard'
import UiButton from '@/components/ui/UiButton'
import UiTruncate from '@/components/ui/UiTruncate'
import { formatDate } from '@/lib/date'

interface Props {
  tournament: TournamentArchive
}

defineProps<Props>()
</script>

<style scoped>
.archive-card {
  height: 100%;
  min-width: 0;
  padding: 0;
  overflow: hidden;
}

.archive-media {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;
  max-height: 200px;
  object-fit: cover;
}

.archive-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
  padding: 1rem 1.25rem;
}

.archive-card-title {
  margin: 0;
  font-weight: 800;
  font-size: 1.1rem;
}

.archive-description {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
  margin: 0;
  min-width: 0;
  line-height: 1.5;
  color: var(--muted-foreground);
  overflow-wrap: anywhere;
}

.archive-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  color: var(--muted-foreground);
}

.archive-date {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.archive-date p,
.archive-count {
  margin: 0;
}

.archive-details-btn {
  width: 100%;
}

.archive-card :deep(.card-footer) {
  padding: 0 1.25rem 1.25rem;
}

@media (max-width: 768px) {
  .archive-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
