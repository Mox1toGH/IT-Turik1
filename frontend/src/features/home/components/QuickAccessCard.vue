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

    <ui-query-block class="panel-body" :query="query">
      <template #error>
        <div class="empty-state">
          <p>Failed to fetch profile info</p>
        </div>
      </template>

      <ui-query-block :query="tournamentsQuery">
        <template #error>
          <div class="empty-state"><p>Failed to fetch tournaments</p></div>
        </template>

        <ui-query-field>
          <template #skeleton>
            <ul class="data-list">
              <li>
                <span>Tournament</span>
                <ui-skeleton variant="rect" width="100%" />
              </li>
              <li>
                <span>Current task</span>
                <ui-skeleton variant="rect" width="100%" />
              </li>
              <li>
                <span>Latest submission</span>
                <ui-skeleton variant="rect" width="100%" />
              </li>
            </ul>
          </template>

          <ul class="data-list">
            <li>
              <span>Tournament</span>
              <RouterLink
                v-if="activeTournament"
                class="quick-link"
                :to="`/tournaments/${activeTournament.id}`"
              >
                {{ activeTournament.name }}
              </RouterLink>
              <span v-else>-</span>
            </li>

            <li>
              <span>Current task</span>
              <ui-query-block v-if="shouldFetchCurrentRound" :query="currentTaskQuery">
                <template #error><span class="text-muted">-</span></template>
                <ui-query-field>
                  <template #skeleton><ui-skeleton variant="rect" width="100%" /></template>
                  <RouterLink
                    v-if="currentRound?.name"
                    class="quick-link"
                    :to="`/tournaments/${activeTournament?.id}?section=rounds`"
                  >
                    {{ currentRound.name }}
                  </RouterLink>
                  <span v-else>-</span>
                </ui-query-field>
              </ui-query-block>
              <span v-else>-</span>
            </li>

            <li>
              <span>Latest submission</span>
              <ui-query-block v-if="hasActiveTournament" :query="submissionsQuery">
                <template #error><span class="text-muted">-</span></template>
                <ui-query-field>
                  <template #skeleton><ui-skeleton variant="rect" width="100%" /></template>
                  <RouterLink
                    v-if="lastSubmission?.round_details?.name"
                    class="quick-link"
                    :to="`/tournaments/${activeTournament?.id}?section=submissions`"
                  >
                    {{ lastSubmission.round_details.name }}
                  </RouterLink>
                  <span v-else>-</span>
                </ui-query-field>
              </ui-query-block>
              <span v-else>-</span>
            </li>
          </ul>
        </ui-query-field>
      </ui-query-block>
    </ui-query-block>
  </ui-card>
</template>

<script setup lang="ts">
import type { UserSummary } from '@/shared/types/user'
import type { QueryLike } from '@/composables/useQueryState'
import {
  useGetCurrentTask,
  useListMyTeamSubmissions,
  useListTournaments,
} from '@/api/tournaments/tournaments'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { computed } from 'vue'

const props = defineProps<{
  user?: UserSummary
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
const hasActiveTournament = computed(() => activeTournament.value !== undefined)

const shouldFetchCurrentRound = computed(() => activeTournament.value?.status === 'running')
const currentTaskQuery = useGetCurrentTask(
  computed(() => ({ tournament_id: activeTournamentId.value })),
  {
    query: {
      enabled: shouldFetchCurrentRound,
      retry: false,
    },
  },
)
const { data: currentRound } = currentTaskQuery

const submissionsQuery = useListMyTeamSubmissions(activeTournamentId, undefined, {
  query: {
    enabled: hasActiveTournament,
  },
})
const { data: submissions } = submissionsQuery

const lastSubmission = computed(() => {
  const list = submissions.value?.items ?? []
  if (list.length === 0) return null
  return list.reduce((latest, current) =>
    new Date(current.created_at).getTime() > new Date(latest.created_at).getTime()
      ? current
      : latest,
  )
})
</script>
