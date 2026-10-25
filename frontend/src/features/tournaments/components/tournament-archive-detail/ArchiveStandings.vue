<template>
  <ui-section title="Final Standings" description="Saved final ranking">
    <div v-if="standings.length" class="table-wrap">
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
    </div>
    <ui-empty-card v-else message="No saved standings." />
  </ui-section>
</template>

<script setup lang="ts">
import UiSection from '@/components/ui/UiSection'
import UiEmptyCard from '@/components/ui/UiEmptyCard'
import { formatScore } from './lib/format'
import type { ArchiveStanding } from '@/features/tournaments/types'

defineProps<{
  standings: ArchiveStanding[]
}>()

const rankClass = (rank: number) => {
  if (rank === 1) return 'rank-gold'
  if (rank === 2) return 'rank-silver'
  if (rank === 3) return 'rank-bronze'
  return ''
}
</script>

<style scoped>
.table-wrap {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
  overflow: hidden;
}

.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 160px;
  gap: 0.5rem;
  padding: 0.65rem 0.85rem;
  border-top: 1px solid var(--border);
  align-items: center;
}

.table-row:first-child {
  border-top: 0;
}

.table-head {
  font-weight: 600;
  color: var(--muted-foreground);
  background: var(--subtle);
}

.rank-pill {
  width: fit-content;
  border-radius: 999px;
  padding: 0.15rem 0.55rem;
  background: var(--subtle);
  color: var(--muted-foreground);
}

.rank-gold .rank-pill {
  background: var(--medal-gold);
  color: var(--medal-gold-fg);
}

.rank-silver .rank-pill {
  background: var(--medal-silver);
  color: var(--medal-silver-fg);
}

.rank-bronze .rank-pill {
  background: var(--medal-bronze);
  color: var(--medal-bronze-fg);
}

.team-link {
  color: var(--foreground);
  text-decoration: none;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
}

.team-link:hover {
  color: var(--primary);
  text-decoration: underline;
}

@media (max-width: 720px) {
  .table-row {
    grid-template-columns: 62px 1fr 95px;
    font-size: 0.83rem;
    padding: 0.6rem;
  }
}
</style>
