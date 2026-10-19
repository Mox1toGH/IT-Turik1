<template>
  <section class="page-shell">
    <ui-query-state :query="archiveQuery">
<template #skeleton>
        <div class="skeleton-stack">
          <ui-skeleton variant="rect" height="260px" />
          <div class="skeleton-stats">
            <ui-skeleton v-for="i in 4" :key="`stats-${i}`" variant="rect" height="96px" />
          </div>
          <ui-skeleton variant="rect" height="220px" />
          <ui-skeleton variant="rect" height="220px" />
        </div>
      </template><div v-if="archive" class="content-stack">
          <archive-hero
            :tournament-id="id"
            :name="archive.name"
            :banner="archive.banner"
            :start-date="archive.start_date"
            :end-date="archive.end_date"
          />

          <ui-section title="Description" description="Tournament summary">
            <p class="description-text">{{ archive.description || 'No description provided.' }}</p>
          </ui-section>

          <ui-tabs :items="tabItems" query-key="tab">
            <template #overview>
              <archive-summary
                :rounds-count="archive.rounds?.length ?? 0"
                :submissions-count="submissions.length"
                :winner-name="winnerName"
              />
            </template>

            <template #standings>
              <archive-standings :standings="archive.standings ?? []" />
            </template>

            <template #rounds>
              <archive-rounds :rounds="archive.rounds ?? []" />
            </template>

            <template #submissions>
              <archive-submissions :submissions="submissions" />
            </template>

            <template #teams>
              <archive-teams :teams="archive.teams ?? []" />
            </template>
          </ui-tabs>
        </div>
</ui-query-state>
  </section>
</template>

<script setup lang="ts">
import UiSection from '@/components/ui/UiSection'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiTabs, { type TabItem } from '@/components/ui/UiTabs'
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
const archiveQuery = useGetTournamentArchive(id)
const { data: archive } = archiveQuery
const { data: submissionsData } = useListTournamentArchiveSubmissions(id)

const submissions = computed(() => submissionsData.value?.items ?? [])

const winnerName = computed(() => {
  const winner = archive.value?.standings?.find((item) => item.rank === 1)
  return winner?.team?.name ?? 'TBD'
})

const tabItems: TabItem[] = [
  { value: 'overview', label: 'Overview' },
  { value: 'standings', label: 'Standings' },
  { value: 'rounds', label: 'Rounds' },
  { value: 'submissions', label: 'Submissions' },
  { value: 'teams', label: 'Teams' },
]
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
  gap: 2rem;
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
</style>
