<template>
  <section class="page-shell">
    <ui-skeleton-loader :loading="isLoading">
      <template #skeleton>
        <div class="skeleton-stack">
          <ui-skeleton variant="rect" height="260px" />
          <div class="skeleton-stats">
            <ui-skeleton v-for="i in 4" :key="`stats-${i}`" variant="rect" height="96px" />
          </div>
          <ui-skeleton variant="rect" height="220px" />
          <ui-skeleton variant="rect" height="220px" />
        </div>
      </template>

      <template #default>
        <div v-if="archive" class="content-stack">
          <archive-hero
            :tournament-id="id"
            :name="archive.name"
            :banner="archive.banner"
            :start-date="archive.start_date"
            :end-date="archive.end_date"
          />

          <ui-card class="section-block">
            <template #header>
              <div class="section-head">
                <h2>Description</h2>
                <p class="section-note">Tournament summary</p>
              </div>
            </template>
            <p class="description-text">{{ archive.description || 'No description provided.' }}</p>
          </ui-card>

          <archive-summary
            :rounds-count="archive.rounds?.length ?? 0"
            :submissions-count="submissions.length"
            :winner-name="winnerName"
          />

          <archive-standings :standings="archive.standings ?? []" />
          <archive-rounds :rounds="archive.rounds ?? []" />
          <archive-submissions :submissions="submissions" />
          <archive-teams :teams="archive.teams ?? []" />
        </div>
      </template>
    </ui-skeleton-loader>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import ArchiveHero from '../components/tournament-archive-detail/ArchiveHero.vue'
import ArchiveSummary from '../components/tournament-archive-detail/ArchiveSummary.vue'
import ArchiveStandings from '../components/tournament-archive-detail/ArchiveStandings.vue'
import ArchiveRounds from '../components/tournament-archive-detail/ArchiveRounds.vue'
import ArchiveSubmissions from '../components/tournament-archive-detail/ArchiveSubmissions.vue'
import ArchiveTeams from '../components/tournament-archive-detail/ArchiveTeams.vue'
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import {
  useGetTournamentArchive,
  useListTournamentArchiveSubmissions,
} from '@/api/tournaments/tournaments'

const route = useRoute()
const id = Number(route.params.id)
const { data: archive, isLoading } = useGetTournamentArchive(id)
const { data: submissionsData } = useListTournamentArchiveSubmissions(id)

const submissions = computed(() => submissionsData.value ?? [])

const winnerName = computed(() => {
  const winner = archive.value?.standings?.find((item) => item.rank === 1)
  return winner?.team?.name ?? 'TBD'
})
</script>

<style scoped>
.page-shell {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-bottom: 1rem;
}

.skeleton-stack {
  display: grid;
  gap: 0.9rem;
}

.skeleton-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.8rem;
}

.content-stack {
  display: grid;
  gap: 1.2rem;
}

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

.description-text {
  margin: 0;
  color: var(--foreground);
  line-height: 1.5;
  overflow-wrap: anywhere;
}

@media (max-width: 980px) {
  .skeleton-stats {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .section-note {
    width: 100%;
  }
}
</style>
