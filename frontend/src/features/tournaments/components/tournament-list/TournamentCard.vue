<template>
  <ui-card class="tournament-card">
    <div class="tournament-top">
      <img
        v-if="tournament.banner"
        class="tournament-banner"
        :src="tournament.banner"
        :alt="`${tournament.name} banner`"
      />
      <h3 class="tournament-title" :title="tournament.name">
        {{ truncateText(tournament.name, 80) }}
      </h3>

      <p class="tournaments-description" :title="tournament.description">
        {{ truncateText(tournament.description, 200) }}
      </p>
    </div>

    <div class="tournament-info">
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
      <ui-button size="sm" asLink :to="`/tournaments/${tournament.id}`" variant="default">
        View details
      </ui-button>
    </template>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { truncateText } from '@/lib/utils'
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
  padding: 0.95rem;
  background: var(--muted);
}

.tournament-top {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  margin-bottom: 0.5rem;
}

.tournament-banner {
  width: 100%;
  aspect-ratio: 16 / 8;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid var(--line-soft);
  background: var(--background);
}

.tournament-title {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
  word-break: break-word;
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
}

.tournaments-description {
  flex: 1;
  margin: 0;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  word-break: break-word;
}

.tournament-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.tournaments-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

.tournaments-date {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tournaments-date p {
  margin: 0;
}

.tournaments-date p:first-child {
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
}
</style>
