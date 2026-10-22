<template>
  <ui-card class="leaderboard-card">
    <template #header>
      <div class="leaderboard-header">
        <div>
          <p class="section-eyebrow">Leaderboard</p>
          <h2>Leaderboard</h2>
          <p class="section-subtitle">Scores and rankings for this tournament.</p>
        </div>

        <ui-popover minWidth="220px" header="Export">
          <template #trigger>
            <ui-button
              size="sm"
              variant="secondary"
              class="export-trigger"
              :disabled="isExportDisabled || isCreatingGoogleSheet"
            >
              Export
            </ui-button>
          </template>

          <template #default="{ close }">
            <div class="export-actions">
              <ui-button
                size="sm"
                variant="secondary"
                class="export-action-btn"
                :disabled="isExportDisabled"
                @click="
                  () => {
                    close()
                    handleDownloadCsv()
                  }
                "
              >
                Download CSV
              </ui-button>

              <ui-button
                size="sm"
                class="export-action-btn"
                :disabled="isExportDisabled || isCreatingGoogleSheet"
                @click="
                  () => {
                    close()
                    void handleOpenInGoogleSheets()
                  }
                "
              >
                {{ isCreatingGoogleSheet ? 'Creating...' : 'Open in Google Sheets' }}
              </ui-button>
            </div>
          </template>
        </ui-popover>
      </div>
    </template>

    <ui-query-block :query="leaderboardQuery">
      <ui-query-field>
        <template #skeleton>
          <leaderboard-skeleton />
        </template>
        <div v-if="rankings.length === 0 || isLeaderboardNotReady" class="leaderboard-empty">
          <p class="text-muted">No leaderboard data yet.</p>
          <p class="text-sm text-muted">Rankings appear once a round has been evaluated.</p>
        </div>
        <leaderboard-table
          v-else
          :rankings="rankings"
          :round-columns="roundColumns"
          :has-round-overflow="hasRoundOverflow"
          :table-vars="tableVars"
          :table-wrap-ref="tableWrapRef"
          :get-round-score="getRoundScore"
          :has-round-participation="hasRoundParticipation"
          :get-round-max-score="getRoundMaxScore"
          :get-entry-max-score="getEntryMaxScore"
          :format-score="formatScore"
          :on-table-wheel="onTableWheel"
          @update:table-wrap-ref="tableWrapRef = $event"
        />
      </ui-query-field>
    </ui-query-block>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiPopover from '@/components/ui/UiPopover'
import LeaderboardSkeleton from './tournament-leaderboard/LeaderboardSkeleton.vue'
import LeaderboardTable from './tournament-leaderboard/LeaderboardTable.vue'
import { computed } from 'vue'
import { useLeaderboard } from '../../../composables/useLeaderboard'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()

const {
  tableWrapRef,
  isCreatingGoogleSheet,
  rankings,
  roundColumns,
  hasRoundOverflow,
  tableVars,
  isLoading,
  isError,
  isFetching,
  error,
  refetch,
  isLeaderboardNotReady,
  isExportDisabled,
  getRoundScore,
  hasRoundParticipation,
  getRoundMaxScore,
  getEntryMaxScore,
  formatScore,
  onTableWheel,
  handleDownloadCsv,
  handleOpenInGoogleSheets,
} = useLeaderboard(() => props.tournamentId)

const leaderboardQuery = computed(() => ({
  isPending: isLoading.value,
  isError: isError.value && !isLeaderboardNotReady.value,
  data: rankings.value,
  error: error.value,
  isFetching: isFetching.value,
  refetch,
}))
</script>

<style scoped>
.leaderboard-card {
  min-width: 0;
}

.leaderboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.leaderboard-header h2 {
  margin: 0.25rem 0;
  font-family: var(--font-display);
  font-weight: 800;
}

.leaderboard-header .section-subtitle {
  margin: 0;
}

.section-eyebrow {
  margin: 0;
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted-foreground);
}

.export-trigger {
  min-width: 7rem;
}

.export-actions {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.export-action-btn {
  justify-content: flex-start;
}
</style>
