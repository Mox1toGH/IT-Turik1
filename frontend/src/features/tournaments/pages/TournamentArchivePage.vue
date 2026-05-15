<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="header">
          <h1>Tournament Archive</h1>
          <ui-button asLink to="/tournaments" size="sm" variant="secondary"
            >Back to active list</ui-button
          >
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div class="grid">
            <ui-skeleton v-for="i in 6" :key="i" variant="rect" height="180px" />
          </div>
        </template>

        <div v-if="items.length" class="grid">
          <ui-card v-for="item in items" :key="item.id" class="archive-card">
            <h3>{{ item.name }}</h3>
            <p class="meta">
              Teams: {{ item.teams.length }} | Results: {{ item.standings.length }}
            </p>
            <p class="description">{{ item.description }}</p>
            <template #footer>
              <ui-button
                asLink
                :to="`/tournaments/archive/${item.id}`"
                size="sm"
                variant="secondary"
              >
                View archive
              </ui-button>
            </template>
          </ui-card>
        </div>

        <p v-else>No finished tournaments yet.</p>
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
import { useListTournamentArchive } from '@/api/tournaments/tournaments'

const { data, isLoading } = useListTournamentArchive()
const items = computed(() => data.value ?? [])
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.meta {
  color: var(--muted-foreground);
}

.description {
  margin: 0;
}

.archive-card {
  background: var(--muted) !important;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
