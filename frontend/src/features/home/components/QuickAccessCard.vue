<template>
  <ui-card class="info-card quick-card">
    <template #header>
      <div>
        <div>
          <h2>Quick access</h2>
          <p class="text-muted">Current tournament links for your team.</p>
        </div>
      </div>
    </template>

    <ui-query-state class="panel-body" :query="query">
      <template #error>
        <div class="empty-state">
          <p>Failed to fetch profile info</p>
        </div>
      </template>

      <ul class="data-list">
        <li>
          <span>Tournament</span>
          <ui-query-state :query="tournamentsQuery">
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
          </ui-query-state>
        </li>

        <li>
          <span>Current task</span>
          <ui-skeleton v-if="isLoadingCurrentRoundBlock" variant="rect" width="100%" />
          <RouterLink
            v-else-if="activeTournament && currentRound?.name"
            class="quick-link"
            :to="`/tournaments/${activeTournament.id}?section=rounds`"
          >
            {{ currentRound.name }}
          </RouterLink>
          <span v-else>{{ currentRound?.name ?? '-' }}</span>
        </li>

        <li>
          <span>Latest submission</span>
          <ui-skeleton v-if="isLoadingSubmissionsBlock" variant="rect" width="100%" />
          <RouterLink
            v-else-if="activeTournament && lastSubmission?.round_details?.name"
            class="quick-link"
            :to="`/tournaments/${activeTournament.id}?section=submissions`"
          >
            {{ lastSubmission.round_details.name }}
          </RouterLink>
          <span v-else>{{ lastSubmission?.round_details?.name ?? '-' }}</span>
        </li>
      </ul>
    </ui-query-state>
  </ui-card>
</template>

<script setup lang="ts">
import type { UserResponse } from '@/api/backendAPINinja.schemas'
import type { QueryLike } from '@/composables/useQueryState'
import {
  useGetCurrentTask,
  useListMyTeamSubmissions,
  useListTournaments,
} from '@/api/tournaments/tournaments'
import UiCard from '@/components/ui/UiCard'
import UiQueryState from '@/components/ui/UiQueryState'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { computed } from 'vue'

const props = defineProps<{
  user?: UserResponse
  query: QueryLike
}>()

const myTeamIds = computed(() => new Set((props.user?.teams ?? []).map((team) => team.id)))

// TODO: add api to get active tournament

const tournamentsQuery = useListTournaments(
  computed(() => ({
    page: 1,
    page_size: 100,
    status: 'registration,running',
  })),
)
const tournamentsResponse = tournamentsQuery.data

const activeTournament = computed(() =>
  (tournamentsResponse.value?.data ?? []).find((tournament) =>
    myTeamIds.value.has(tournament.registered_team?.id ?? -1),
  ),
)
const activeTournamentId = computed(() => activeTournament.value?.id ?? 0)

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
  () =>
    tournamentsQuery.isLoading.value ||
    (shouldFetchCurrentRound.value && isLoadingCurrentRound.value),
)

const { data: submissions, isLoading: isLoadingSubmissions } =
  useListMyTeamSubmissions(activeTournamentId)

const isLoadingSubmissionsBlock = computed(
  () => tournamentsQuery.isLoading.value || isLoadingSubmissions.value,
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
