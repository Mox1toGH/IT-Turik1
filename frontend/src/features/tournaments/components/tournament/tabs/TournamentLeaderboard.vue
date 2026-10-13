<template>
  <ui-section
    title="Leaderboard"
    description="Scores and rankings for this tournament."
    class="leaderboard-shell"
  >
    <template #actions>
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
    </template>

    <ui-skeleton-loader :loading="isLoading">
      <template #skeleton>
        <leaderboard-skeleton />
      </template>

      <ui-card v-if="isError && !isLeaderboardNotReady" class="empty">
        <p>{{ errorMessage }}</p>
      </ui-card>

      <ui-card v-else-if="rankings.length === 0 || isLeaderboardNotReady" class="empty">
        <p>No leaderboard data yet.</p>
      </ui-card>

      <template v-else>
        <leaderboard-table
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
      </template>
    </ui-skeleton-loader>
  </ui-section>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiPopover from '@/components/ui/UiPopover'
import UiSection from '@/components/ui/UiSection'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import LeaderboardSkeleton from './tournament-leaderboard/LeaderboardSkeleton.vue'
import LeaderboardTable from './tournament-leaderboard/LeaderboardTable.vue'
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
  errorMessage,
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
</script>

<style scoped>
.leaderboard-shell {
  min-width: 0;
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

.empty {
  display: flex;
  height: 220px;
  align-items: center;
  justify-content: center;
}
</style>
