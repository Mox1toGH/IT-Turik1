<template>
  <div
    ref="wrapEl"
    class="leaderboard-table-wrap"
    :class="{ 'is-rounds-scroll-capped': hasRoundOverflow }"
    @wheel="onTableWheel"
  >
    <table class="leaderboard-table" :style="tableVars">
      <thead>
        <tr>
          <th class="rank-col sticky-left">Place</th>
          <th class="team-col sticky-left">Team</th>
          <th v-for="round in roundColumns" :key="round.id" class="round-col">
            {{ round.name }}
          </th>
          <th class="total-col sticky-right">Total</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="entry in rankings" :key="entry.team_id">
          <td class="rank-col sticky-left">{{ entry.rank }}</td>
          <td class="team-col sticky-left">
            <RouterLink :to="`/teams/${entry.team_id}`" class="team-link">{{
              entry.team_name
            }}</RouterLink>
          </td>
          <td
            v-for="round in roundColumns"
            :key="`${entry.team_id}-${round.id}`"
            class="round-cell"
          >
            <template v-if="hasRoundParticipation(entry, round.id)">
              {{ formatScore(getRoundScore(entry, round.id) ?? 0) }}/{{
                formatScore(getRoundMaxScore(entry, round.id) ?? 0)
              }}
            </template>
            <span v-else class="missed-round">x</span>
          </td>
          <td class="total-col sticky-right total-value">
            {{ formatScore(entry.total_score) }}/{{ formatScore(getEntryMaxScore(entry)) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <p v-if="hasRoundOverflow" class="scroll-hint">Scroll horizontally to view all rounds.</p>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import type {
  LeaderboardRoundColumn,
  LeaderboardTournamentEntry,
} from '../../../../composables/useLeaderboard'

const props = defineProps<{
  rankings: LeaderboardTournamentEntry[]
  roundColumns: LeaderboardRoundColumn[]
  hasRoundOverflow: boolean
  tableVars: Record<string, string>
  tableWrapRef: HTMLElement | null
  getRoundScore: (entry: LeaderboardTournamentEntry, roundId: number) => number | null
  hasRoundParticipation: (entry: LeaderboardTournamentEntry, roundId: number) => boolean
  getRoundMaxScore: (entry: LeaderboardTournamentEntry, roundId: number) => number | null
  getEntryMaxScore: (entry: LeaderboardTournamentEntry) => number
  formatScore: (value: number) => string
  onTableWheel: (event: WheelEvent) => void
}>()

const emit = defineEmits<{
  (e: 'update:tableWrapRef', value: HTMLElement | null): void
}>()

const wrapEl = ref<HTMLElement | null>(null)
watch(wrapEl, (el) => {
  if (el !== props.tableWrapRef) emit('update:tableWrapRef', el)
})
</script>

<style scoped>
.leaderboard-table-wrap {
  position: relative;
  isolation: isolate;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

.leaderboard-table-wrap.is-rounds-scroll-capped {
  max-width: min(100%, calc(5.5rem + 15rem + (var(--visible-round-cols) * 7.5rem) + 10rem));
}

.leaderboard-table {
  width: 100%;
  min-width: calc(5.5rem + 15rem + (var(--round-cols) * 7.5rem) + 10rem);
  border-collapse: separate;
  border-spacing: 0;
}

.leaderboard-table th,
.leaderboard-table td {
  padding: 0.75rem 0.8rem;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
  background: var(--card);
}

.leaderboard-table thead th {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--muted-foreground);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  background: var(--subtle);
  position: sticky;
  top: 0;
  z-index: 10;
  overflow: hidden;
  text-overflow: ellipsis;
}

.leaderboard-table tbody tr:hover td {
  background: var(--hover);
}

.rank-col {
  width: 5.5rem;
  min-width: 5.5rem;
  text-align: center;
  font-weight: 700;
}

.team-col {
  width: 15rem;
  min-width: 15rem;
  max-width: 15rem;
}

.round-col,
.round-cell {
  width: 7.5rem;
  min-width: 7.5rem;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.total-col {
  width: 10rem;
  min-width: 10rem;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.total-value {
  font-weight: 700;
}

.sticky-left,
.sticky-right {
  position: sticky;
  z-index: 5;
  background: var(--card);
}

.leaderboard-table thead .sticky-left,
.leaderboard-table thead .sticky-right {
  z-index: 12;
}

.leaderboard-table thead .rank-col.sticky-left {
  z-index: 13;
}

.rank-col.sticky-left {
  left: 0;
  box-shadow: 1px 0 0 var(--border);
}

.team-col.sticky-left {
  left: 5.5rem;
  box-shadow: 1px 0 0 var(--border);
}

.total-col.sticky-right {
  right: 0;
  box-shadow: -1px 0 0 var(--border);
}

.team-link {
  color: var(--foreground);
  text-decoration: none;
  font-weight: 600;
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

.team-link:hover,
.team-link:focus-visible {
  color: var(--primary);
  text-decoration: underline;
}

.missed-round {
  display: inline-block;
  color: var(--muted-foreground);
  font-weight: 700;
}

.scroll-hint {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  text-align: right;
  color: var(--muted-foreground);
}

@media (max-width: 900px) {
  .team-col {
    width: 12rem;
    min-width: 12rem;
    max-width: 12rem;
  }

  .leaderboard-table {
    min-width: calc(5rem + 12rem + (var(--round-cols) * 7rem) + 9rem);
  }

  .leaderboard-table-wrap.is-rounds-scroll-capped {
    max-width: min(100%, calc(5rem + 12rem + (var(--visible-round-cols) * 7rem) + 9rem));
  }

  .rank-col {
    width: 5rem;
    min-width: 5rem;
  }

  .team-col.sticky-left {
    left: 5rem;
  }

  .round-col,
  .round-cell {
    width: 7rem;
    min-width: 7rem;
  }

  .total-col {
    width: 9rem;
    min-width: 9rem;
  }
}
</style>
