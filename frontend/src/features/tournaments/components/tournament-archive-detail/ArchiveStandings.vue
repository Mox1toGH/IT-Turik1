<template>
  <ui-card class="section-block">
    <template #header>
      <div class="section-head">
        <h2>Final Standings</h2>
        <p class="section-note">Saved final ranking</p>
      </div>
    </template>
    <ui-card v-if="standings.length" class="table-wrap">
      <div class="table-row table-head">
        <span>Rank</span>
        <span>Team</span>
        <span>Total Score</span>
      </div>
      <div
        v-for="row in standings"
        :key="`${row.rank}-${row.team.id}`"
        class="table-row"
        :class="rankClass(row.rank)"
      >
        <span class="rank-pill">#{{ row.rank }}</span>
        <router-link :to="`/teams/${row.team.id}`" class="team-link">
          {{ row.team.name }}
        </router-link>
        <span>{{ formatScore(row.total_score) }}</span>
      </div>
    </ui-card>
    <ui-card v-else>
      <p class="empty-state">No saved standings.</p>
    </ui-card>
  </ui-card>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import { formatScore } from './lib/format'
import type { TournamentArchiveDetailResponse } from '@/api/backendAPINinja.schemas'

defineProps<{
  standings: TournamentArchiveDetailResponse['standings']
}>()

const rankClass = (rank: number) => {
  if (rank === 1) return 'rank-gold'
  if (rank === 2) return 'rank-silver'
  if (rank === 3) return 'rank-bronze'
  return ''
}
</script>

<style scoped>
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

.table-wrap {
  overflow: hidden;
  padding: 0;
  border: 1px solid var(--line-soft);
}

.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 160px;
  gap: 0.5rem;
  padding: 0.65rem 0.85rem;
  border-top: 1px solid color-mix(in srgb, var(--line-soft) 85%, transparent);
  align-items: center;
}

.table-head {
  border-top: 0;
  font-weight: 600;
  background: var(--muted);
}

.rank-pill {
  width: fit-content;
  border-radius: 999px;
  padding: 0.15rem 0.55rem;
  background: color-mix(in srgb, var(--muted) 65%, transparent);
}

.rank-gold .rank-pill {
  background: #f6d365;
  color: #3a2d00;
}

.rank-silver .rank-pill {
  background: #dce1e8;
  color: #1f2937;
}

.rank-bronze .rank-pill {
  background: #e8b28d;
  color: #4b2a12;
}

.empty-state {
  margin: 0;
  color: var(--muted-foreground);
}

@media (max-width: 720px) {
  .section-note {
    width: 100%;
  }

  .table-row {
    grid-template-columns: 62px 1fr 95px;
    font-size: 0.83rem;
    padding: 0.6rem;
  }
}
</style>
