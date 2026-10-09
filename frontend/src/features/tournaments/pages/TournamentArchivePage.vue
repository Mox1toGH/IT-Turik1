<template>
  <section class="page-shell">
    <section class="archive-section">
      <header class="page-header">
        <div class="archive-header">
          <div class="title-row">
            <h1 class="archive-title">Tournament Archive</h1>
          </div>
          <div class="header-actions">
            <ui-button asLink to="/tournaments" size="sm" variant="secondary"
              >Back to active list</ui-button
            >
          </div>
        </div>
      </header>

      <ui-skeleton-loader :loading="isLoading">
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

        <div v-if="tournaments" class="archive-grid">
          <tournament-archive-card
            v-for="tournament in tournaments"
            :key="tournament.id"
            :tournament="tournament"
          />
        </div>

        <ui-card v-else class="empty-card">
          <p class="empty-error">No finished tournaments yet.</p>
        </ui-card>
      </ui-skeleton-loader>
    </section>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { useListTournamentArchive } from '@/api/tournaments/tournaments'
import TournamentArchiveCard from '../components/tournament-archive/TournamentArchiveCard.vue'

const { data: tournaments, isLoading } = useListTournamentArchive()
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

.header-actions {
  display: flex;
  gap: 8px;
}

.archive-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

/* Потрібні для скелетона */
.archive-card {
  background: var(--muted) !important;
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

.empty-card {
  margin-top: 0.5rem;
}

.empty-error {
  margin: 0;
}

@media (max-width: 900px) {
  .archive-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .archive-grid {
    grid-template-columns: 1fr;
  }

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
