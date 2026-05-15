<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
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
      </template>

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

        <div v-if="items.length" class="archive-grid">
          <ui-card v-for="item in items" :key="item.id" class="archive-card">
            <div
              class="archive-top"
              :class="{ 'archive-top--with-banner': Boolean(item.banner) }"
              :style="
                item.banner
                  ? {
                      backgroundImage: `linear-gradient(rgba(5, 11, 23, 0.72), rgba(5, 11, 23, 0.45)), url(${item.banner})`,
                    }
                  : {}
              "
            >
              <h3 class="archive-card-title" :title="item.name">
                {{ truncateText(item.name, 80) }}
              </h3>
              <p class="archive-description" :title="item.description">
                {{ truncateText(item.description || 'No description provided.', 180) }}
              </p>
            </div>

            <div class="archive-info">
              <div class="archive-meta">
                <div class="archive-date">
                  <p>Finished:</p>
                  <p>{{ formatDate(item.end_date) }}</p>
                </div>
                <p class="archive-count">
                  {{ item.standings.length }} standings
                </p>
              </div>
            </div>
            <template #footer>
              <ui-button
                asLink
                :to="`/tournaments/archive/${item.id}`"
                size="sm"
                variant="secondary"
                class="archive-details-btn"
              >
                View archive
              </ui-button>
            </template>
          </ui-card>
        </div>

        <ui-card v-else class="empty-card">
          <p class="empty-error">No finished tournaments yet.</p>
        </ui-card>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { computed } from 'vue'
import { truncateText } from '@/lib/utils'
import { formatDate } from '@/lib/date'
import { useListTournamentArchive } from '@/api/tournaments/tournaments'

const { data, isLoading } = useListTournamentArchive()
const items = computed(() => data.value ?? [])
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
