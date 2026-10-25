<template>
  <section class="page-shell">
    <section class="archive-section">
      <page-back-link to="/tournaments" label="Back to active tournaments" />
      <header class="page-header">
        <div class="archive-header">
          <div class="title-row">
            <h1 class="archive-title">Tournament Archive</h1>
          </div>
        </div>
      </header>

      <ui-query-block :query="archiveQuery">
        <ui-query-field>
          <template #skeleton>
            <div class="archive-grid">
              <ui-card v-for="i in 6" :key="i" class="archive-card">
                <template #header>
                  <ui-skeleton variant="rect" width="70%" height="24px" />
                </template>
                <ui-skeleton variant="rect" class="archive-description" height="56px" />
                <div class="archive-meta">
                  <div class="archive-date">
                    <ui-skeleton variant="rect" width="70px" />
                    <ui-skeleton variant="rect" width="150px" />
                  </div>
                  <ui-skeleton variant="rect" width="90px" height="28px" />
                </div>
                <ui-skeleton variant="rect" width="100%" height="36px" />
              </ui-card>
            </div>
          </template>

          <template #default>
            <ui-empty-card v-if="isEmpty" message="No finished tournaments yet." />
            <div v-else class="archive-grid">
              <tournament-archive-card
                v-for="tournament in tournamentItems"
                :key="tournament.id"
                :tournament="tournament"
              />
            </div>
          </template>
        </ui-query-field>
      </ui-query-block>
    </section>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiEmptyCard from '@/components/ui/UiEmptyCard'
import PageBackLink from '@/components/shared/PageBackLink.vue'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import { computed } from 'vue'
import { useListTournamentArchive } from '@/api/tournaments/tournaments'
import TournamentArchiveCard from '../components/tournament-archive/TournamentArchiveCard.vue'

const archiveQuery = useListTournamentArchive()
const { data: tournaments } = archiveQuery
const tournamentItems = computed(() => tournaments.value?.items ?? [])
const isEmpty = computed(() => tournamentItems.value.length === 0)
</script>

<style scoped>
.archive-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.archive-title {
  margin: 0;
}

.archive-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
}

.archive-description {
  flex: 1;
  margin-bottom: 0;
  line-height: 1.5;
  word-break: break-word;
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

@media (max-width: 768px) {
  .archive-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .archive-header {
    flex-direction: column;
    align-items: start;
  }
}
</style>
