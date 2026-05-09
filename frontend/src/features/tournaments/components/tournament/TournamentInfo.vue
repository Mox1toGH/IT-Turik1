<template>
  <ui-card class="tournament-card" :is-error="isError">
    <template #header>
      <div class="tournament-header">
        <h2>Tournament Info</h2>

        <ui-button v-if="tournament?.status === 'draft'" size="sm" @click="handleStartRegistration"
          ><loading-icon v-if="isPending" />Start registration</ui-button
        >
      </div>
    </template>

    <template #error>
      <div style="display: flex; height: 300px; justify-content: center; align-items: center">
        <p>Error while fetching tournament info (code: {{ error?.code }})</p>
      </div>
    </template>

    <div class="tournament-info">
      <div class="tournament-name">
        <p class="text-muted">Name</p>
        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 0.3rem">
              <ui-skeleton variant="rect" width="100%" />
              <ui-skeleton variant="rect" width="80%" />
            </div>
          </template>

          <p :title="tournament?.name">{{ truncateText(tournament?.name ?? '', 200) }}</p>
        </ui-skeleton-loader>
      </div>

      <div class="tournament-description">
        <p class="text-muted">Description</p>

        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 0.4rem">
              <ui-skeleton variant="rect" width="90%" />
              <ui-skeleton variant="rect" width="70%" />
              <ui-skeleton variant="rect" width="80%" />
            </div>
          </template>

          <large-text-modal
            v-model="isDesciptionOpen"
            title="Tournament description"
            :text="tournament?.description ?? ''"
            max-length="190"
          >
            <template #trigger="{ toggleOpen }">
              <p
                :title="tournament?.description"
                @click="toggleOpen"
                :class="['tournament-description-text', { large: isDescriptionLarge }]"
              >
                {{ truncateText(tournament?.description ?? '', 190) }}
              </p>
            </template>
          </large-text-modal>
        </ui-skeleton-loader>
      </div>

      <div class="tournament-dates">
        <div>
          <p class="text-muted">Start / end date</p>
          <div class="">
            <ui-skeleton-loader :loading="isLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="180px" />
              </template>

              <p>
                {{
                  tournament?.start_date
                    ? formatDate(tournament.start_date, { showHours: true })
                    : '-'
                }}
              </p>
              <p>
                {{
                  tournament?.end_date ? formatDate(tournament.end_date, { showHours: true }) : '-'
                }}
              </p>
            </ui-skeleton-loader>
          </div>
        </div>

        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="100px" />
          </template>

          <ui-badge :variant="tournamentStatusBadge(tournament?.status)">{{
            tournament?.status
          }}</ui-badge>
        </ui-skeleton-loader>
      </div>
    </div>

    <div class="tournament-action">
      <ui-button
        v-if="currentRound"
        asLink
        :to="`/tournaments/1?section=rounds`"
        variant="ghost"
        class="tournament-action-btn"
      >
        Current round: {{ currentRound.name }}
      </ui-button>

      <join-tournament-btn
        v-if="tournament?.status === 'registration'"
        :tournament-id="props.tournamentId"
        :registered-team-id="tournament?.registered_team?.id ?? null"
      />
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { parseApiError } from '@/api/errors'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { computed, ref } from 'vue'
import { tournamentStatusBadge, truncateText } from '@/lib/utils'
import { formatDate } from '@/lib/date'
import { useCurrentRound, useStartRegistration, useTournamentInfo } from '@/api/queries/tournaments'
import JoinTournamentBtn from './JoinTournamentBtn.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import LargeTextModal from '../../../../components/shared/LargeTextModal.vue'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const isDesciptionOpen = ref(false)
const isDescriptionLarge = computed(() => (tournament.value?.description.length ?? 0) > 190)

const {
  data: tournament,
  isLoading,
  error: tournamentInfoError,
  isError,
} = useTournamentInfo({ id: props.tournamentId })
const error = computed(() => parseApiError(tournamentInfoError.value))
const { data: currentRound } = useCurrentRound(
  { id: props.tournamentId },
  {
    enabled: computed(() => tournament.value?.status === 'running'),
  },
)

const { mutate: startRegistration, isPending } = useStartRegistration()
const handleStartRegistration = () => {
  startRegistration({
    tournamentId: props.tournamentId,
  })
}
</script>

<style scoped>
.tournament-card {
  flex: 1;
}

.tournament-header {
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-timeline {
  display: flex;
  gap: 0.3rem;
}

.tournament-info {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.tournament-name,
.tournament-dates,
.tournament-description {
  padding-bottom: 0.7rem;
  border-bottom: 1px solid var(--border);
}

.tournament-description-text {
  border-radius: 6px;
  transition: baclground 2s ease-in;
  word-break: break-word;
}

.tournament-dates {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tournament-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.7rem;
}

.tournament-action {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tournament-action-btn {
  width: 100%;
}
</style>
