<template>
  <ui-card class="tournament-card">
    <img
      v-if="tournament.banner"
      class="tournament-media"
      :src="tournament.banner"
      :alt="`${tournament.name} banner`"
    />

    <div class="tournament-body">
      <ui-truncate :text="tournament.name" class="tournament-title" />

      <p class="tournaments-description">{{ tournament.description }}</p>

      <div class="tournaments-meta">
        <div class="tournaments-date">
          <p>Start date:</p>
          <p>{{ formatDate(tournament.start_date) }}</p>
        </div>

        <ui-badge :variant="statusBadgeVariant(tournament.status)">
          {{ tournament.status }}
        </ui-badge>
      </div>
    </div>

    <template #footer>
      <ui-button
        size="sm"
        asLink
        :to="`/tournaments/${tournament.id}`"
        variant="default"
        class="tournament-action"
      >
        View details
      </ui-button>
    </template>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiTruncate from '@/components/ui/UiTruncate'
import { formatDate } from '@/lib/date'
import type { TournamentResponse, TournamentStatus } from '@/api/backendAPINinja.schemas'

defineProps<{
  tournament: TournamentResponse
}>()

const statusBadgeVariant = (status?: TournamentStatus) => {
  if (status === 'running') return 'green'
  if (status === 'registration') return 'orange'

  return 'gray'
}
</script>

<style scoped>
.tournament-card {
  height: 100%;
  min-width: 0;
  padding: 0;
  overflow: hidden;
}

.tournament-media {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;
  max-height: 200px;
  object-fit: cover;
}

.tournament-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
  padding: 1rem 1.25rem;
}

.tournament-title {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.tournaments-description {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
  margin: 0;
  min-width: 0;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  overflow-wrap: anywhere;
}

.tournaments-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

.tournaments-date {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.tournaments-date p {
  margin: 0;
}

.tournaments-date p:first-child {
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
}

.tournament-action {
  width: 100%;
}

.tournament-card :deep(.card-footer) {
  padding: 0 1.25rem 1.25rem;
}
</style>
