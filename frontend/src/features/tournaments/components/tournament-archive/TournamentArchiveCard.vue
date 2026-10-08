<template>
  <ui-card class="archive-card">
    <div
      class="archive-top"
      :class="{ 'archive-top--with-banner': Boolean(tournament.banner) }"
      :style="
        tournament.banner
          ? {
              backgroundImage: `linear-gradient(rgba(5, 11, 23, 0.72), rgba(5, 11, 23, 0.45)), url(${tournament.banner})`,
            }
          : {}
      "
    >
      <h3 class="archive-card-title" :title="tournament.name">
        {{ truncateText(tournament.name, 80) }}
      </h3>
      <p class="archive-description" :title="tournament.description">
        {{ truncateText(tournament.description || 'No description provided.', 180) }}
      </p>
    </div>

    <div class="archive-info">
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
import type { TournamentArchiveListResponse } from '@/api/backendAPINinja.schemas'
import UiCard from '@/components/ui/UiCard.vue'
import { formatDate } from '@/lib/date'
import { truncateText } from '@/lib/utils'

interface Props {
  tournament: TournamentArchiveListResponse
}

defineProps<Props>()
</script>

<style scoped>
.archive-card {
  background: var(--muted) !important;
}

.archive-top {
  border-radius: 12px;
  padding: 12px;
  margin: -4px -4px 12px;
  background: color-mix(in srgb, var(--muted) 90%, #000 10%);
  background-size: cover;
  background-position: center;
  min-height: 140px;
  display: flex;
  flex-direction: column;
}

.archive-top--with-banner {
  color: #fff;
}

.archive-card-title {
  margin: 0;
  word-break: break-word;
}

.archive-description {
  flex: 1;
  margin-bottom: 0;
  line-height: 1.5;
  word-break: break-word;
}

.archive-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.archive-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  color: var(--muted-foreground);
}

.archive-date {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.archive-date p,
.archive-count {
  margin: 0;
}

.archive-details-btn {
  width: 100%;
}

@media (max-width: 768px) {
  .archive-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
