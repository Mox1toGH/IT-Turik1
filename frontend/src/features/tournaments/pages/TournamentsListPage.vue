<template>
  <section class="tournaments-page page-shell">
    <tournaments-hero :is-admin="isAdmin" />

    <div class="tournaments-rule" aria-hidden="true"></div>

    <tournament-filters
      v-model:status="statusFilter"
      :status-options="statusOptions"
      @search="onSearch"
    />

    <section class="tournaments-section" aria-label="Tournaments">
      <div v-if="isStale && status === 'data'" class="stale-banner" role="status">
        <span>Update failed</span>
        <button type="button" :disabled="isFetching" @click="() => refetch()">
          {{ isFetching ? 'Retrying…' : 'Retry' }}
        </button>
      </div>

      <div v-if="status === 'loading'" class="tournaments-grid">
        <div v-for="i in pageSize" :key="i" class="tournament-card-skeleton">
          <ui-skeleton variant="rect" class="skeleton-media" />
          <div class="skeleton-body">
            <ui-skeleton variant="rect" width="70%" height="24px" />
            <ui-skeleton variant="rect" width="100%" height="32px" />
            <div class="tournaments-meta">
              <ui-skeleton variant="rect" width="130px" />
              <ui-skeleton variant="rect" width="90px" height="28px" />
            </div>
            <ui-skeleton variant="rect" width="100%" height="36px" />
          </div>
        </div>
      </div>

      <div v-else-if="status === 'error'" class="tournaments-state">
        <p v-if="errorCode === 'network' && !isOnline" class="card-muted">
          Waiting for connection…
        </p>
        <ui-card-error
          v-else
          title="tournaments"
          :error-code="errorCode"
          :is-fetching="isFetching"
          @retry="refetch"
        />
      </div>

      <div v-else-if="status === 'empty'" class="tournaments-state">
        <p class="card-muted">No tournaments found</p>
        <p class="text-base text-muted">Try changing the search text or status filters.</p>
      </div>

      <div v-else :class="{ dimmed: isFetching }" :aria-busy="isFetching || undefined">
        <div v-if="tournaments?.total" class="tournaments-grid">
          <tournament-card
            v-for="tournament in tournaments.data"
            :key="tournament.id"
            :tournament="tournament"
          />
        </div>

        <ui-pagination
          class="tournaments-pagination"
          v-if="(tournaments?.total ?? 0) > pageSize"
          v-model="currentPage"
          :total-items="tournaments?.total ?? 0"
          :page-size="pageSize"
        />
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { keepPreviousData } from '@tanstack/vue-query'
import UiCardError from '@/components/ui/UiCardError'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiPagination from '@/components/ui/UiPagination'
import { useCardState } from '@/composables/useCardState'
import { useConnection } from '@/composables/useConnection'
import TournamentsHero from '../components/tournament-list/TournamentsHero.vue'
import TournamentFilters from '../components/tournament-list/TournamentFilters.vue'
import TournamentCard from '../components/tournament-list/TournamentCard.vue'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useListTournaments } from '@/api/tournaments/tournaments'
import type { ListTournamentsParams, TournamentStatus } from '@/api/backendAPINinja.schemas'

const currentPage = ref(1)
const pageSize = 12
const searchQuery = ref('')
const statusFilter = ref<TournamentStatus[]>([])

const { data: user } = useGetUserProfile()
const isAdmin = computed(() => user.value?.role === 'admin')
const { isOnline } = useConnection()

const statusOptions = computed(() => {
  const base = [
    { label: 'Draft', value: 'draft' },
    { label: 'Registration', value: 'registration' },
    { label: 'Running', value: 'running' },
    { label: 'Finished', value: 'finished' },
  ]

  return isAdmin.value ? base : base.filter((option) => option.value !== 'draft')
})

const params = computed<ListTournamentsParams>(() => ({
  page: currentPage.value,
  searchQuery: searchQuery.value,
  page_size: pageSize,
  status: statusFilter.value.join(','),
}))

const tournamentsQuery = useListTournaments(params, {
  query: { staleTime: 1000 * 60 * 5, placeholderData: keepPreviousData },
})

const { data: tournaments, isFetching, refetch } = tournamentsQuery
const { status, errorCode, isStale } = useCardState(tournamentsQuery)

const onSearch = (query: string) => {
  currentPage.value = 1
  searchQuery.value = query
}

watch(statusFilter, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.tournaments-page {
  gap: 1.4rem;
}

.tournaments-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--border);
}

.tournaments-section {
  display: grid;
  gap: 1rem;
  min-width: 0;
}

.tournaments-pagination {
  margin-top: 1rem;
}

.tournaments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
}

.tournament-card-skeleton {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

.skeleton-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
}

.skeleton-media {
  width: 100%;
  aspect-ratio: 16 / 9;
  max-height: 200px;
  height: auto;
  border-radius: 0;
}

.tournaments-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.tournaments-state {
  display: grid;
  gap: 0.5rem;
  justify-items: center;
  text-align: center;
  padding: 2rem 0;
}

.card-muted {
  margin: 0;
  font-size: 0.9rem;
  color: var(--muted-foreground);
}

.dimmed > * {
  opacity: 0.6;
}

.stale-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.35rem 0.6rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--subtle);
  color: var(--muted-foreground);
  font-size: 0.8rem;
}

.stale-banner button {
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  font-weight: 600;
  text-decoration: underline;
  cursor: pointer;
}

.stale-banner button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.stale-banner button:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}

@media (max-width: 760px) {
  .tournaments-page {
    padding: 1rem 1rem 2rem;
  }
}
</style>
