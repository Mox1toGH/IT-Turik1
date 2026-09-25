<template>
  <ui-card class="info-card quick-card" variant="form" :is-error="isLoadingUserError">
    <template #error>
      <div class="empty-state">
        <p>Failed to fetch profile info</p>
      </div>
    </template>

    <template #header>
      <div>
        <div>
          <h2>Quick access</h2>
          <p class="text-muted">Current tournament links for your team.</p>
        </div>
      </div>
    </template>

    <div class="panel-body">
      <ul class="data-list">
        <li>
          <span>Tournament</span>
          <ui-skeleton-loader :loading="isLoadingTournament">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" />
            </template>
            <RouterLink
              v-if="activeTournament"
              class="quick-link"
              :to="`/tournaments/${activeTournament.id}`"
            >
              {{ activeTournament.name }}
            </RouterLink>
            <span v-else>-</span>
          </ui-skeleton-loader>
        </li>

        <li>
          <span>Current task</span>
          <ui-skeleton-loader :loading="isLoadingCurrentRoundBlock">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" />
            </template>
            <RouterLink
              v-if="activeTournament && currentRound?.name"
              class="quick-link"
              :to="`/tournaments/${activeTournament.id}?section=rounds`"
            >
              {{ currentRound.name }}
            </RouterLink>
            <span v-else>{{ currentRound?.name ?? '-' }}</span>
          </ui-skeleton-loader>
        </li>

        <li>
          <span>Latest submission</span>
          <ui-skeleton-loader :loading="isLoadingSubmissionsBlock">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" />
            </template>
            <RouterLink
              v-if="activeTournament && lastSubmission?.round_details?.name"
              class="quick-link"
              :to="`/tournaments/${activeTournament.id}?section=submissions`"
            >
              {{ lastSubmission.round_details.name }}
            </RouterLink>
            <span v-else>{{ lastSubmission?.round_details?.name ?? '-' }}</span>
          </ui-skeleton-loader>
        </li>
      </ul>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import type { UserResponse } from '@/api/backendAPINinja.schemas'
import {
  useGetCurrentTask,
  useListMyTeamSubmissions,
  useListTournaments,
} from '@/api/tournaments/tournaments'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { computed } from 'vue'

const props = defineProps<{
  user?: UserResponse
  isLoadingUserError: boolean
  isLoadingUser: boolean
}>()

const myTeamIds = computed(() => new Set((props.user?.teams ?? []).map((team) => team.id)))

// TODO: add api to get active tournament

const { data: tournamentsResponse, isLoading: isLoadingActiveTournament } = useListTournaments(
  computed(() => ({
    page: 1,
    page_size: 100,
    status: 'registration,running',
  })),
)

const activeTournament = computed(() =>
  (tournamentsResponse.value?.data ?? []).find((tournament) =>
    myTeamIds.value.has(tournament.registered_team?.id ?? -1),
  ),
)
const activeTournamentId = computed(() => activeTournament.value?.id ?? 0)

const isLoadingTournament = computed(() => props.isLoadingUser || isLoadingActiveTournament.value)

const shouldFetchCurrentRound = computed(() => activeTournament.value?.status === 'running')
const { data: currentRound, isLoading: isLoadingCurrentRound } = useGetCurrentTask(
  { tournament_id: activeTournamentId.value },
  {
    query: {
      enabled: shouldFetchCurrentRound,
      retry: false,
    },
  },
)

const isLoadingCurrentRoundBlock = computed(
  () => isLoadingTournament.value || (shouldFetchCurrentRound.value && isLoadingCurrentRound.value),
)

const { data: submissions, isLoading: isLoadingSubmissions } =
  useListMyTeamSubmissions(activeTournamentId)

const isLoadingSubmissionsBlock = computed(
  () => isLoadingTournament.value || isLoadingSubmissions.value,
)

const lastSubmission = computed(() => {
  const list = submissions.value ?? []
  if (list.length === 0) return null
  return list.reduce((latest, current) =>
    new Date(current.created_at).getTime() > new Date(latest.created_at).getTime()
      ? current
      : latest,
  )
})
</script>
