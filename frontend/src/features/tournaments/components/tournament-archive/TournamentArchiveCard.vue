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
