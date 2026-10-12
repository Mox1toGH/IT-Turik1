<template>
  <section class="tournaments-page page-shell">
    <tournaments-hero :total="tournaments?.total ?? 0" :loading="isLoading" :is-admin="isAdmin" />

    <div class="tournaments-rule" aria-hidden="true"></div>

    <section class="tournaments-section">
      <ui-card
        variant="panel"
        class="tournaments-panel"
        :status="status"
        :is-fetching="isFetching"
        :is-stale="isStale"
        :error-code="errorCode"
        empty-text="No tournaments found"
        @retry="refetch"
      >
        <template #header>
          <div class="section-head">
            <div>
              <p class="section-eyebrow">Discover</p>
              <h2 class="text-3xl">Active tournaments</h2>
              <p class="section-subtitle text-base">
                Filter competitions by name or registration status.
              </p>
            </div>
          </div>

          <tournament-filters
            v-model:status="statusFilter"
            :status-options="statusOptions"
            @search="onSearch"
          />
        </template>

        <template #skeleton>
          <div class="tournaments-grid">
            <ui-card v-for="i in pageSize" :key="i" class="tournament-card">
              <template #header>
                <ui-skeleton variant="rect" width="70%" height="24px" />
              </template>

              <ui-skeleton variant="rect" class="tournaments-description" height="48px" />

              <div class="tournaments-meta">
                <div class="tournaments-date">
                  <ui-skeleton variant="rect" width="60px" />
                  <ui-skeleton variant="rect" width="130px" />
                </div>

                <ui-skeleton variant="rect" width="120px" height="28px" />
              </div>

              <ui-skeleton variant="rect" width="100%" height="36px" />
            </ui-card>
          </div>
        </template>

        <template #empty-action>
          <p class="text-base text-muted">Try changing the search text or status filters.</p>
        </template>

        <div v-if="tournaments?.total" class="tournaments-grid">
          <tournament-card
            v-for="tournament in tournaments.data"
            :key="tournament.id"
            :tournament="tournament"
          />
        </div>

        <template #footer>
          <ui-pagination
            v-if="status === 'data' && (tournaments?.total ?? 0) > pageSize"
            v-model="currentPage"
            :total-items="tournaments?.total ?? 0"
            :page-size="pageSize"
          />
        </template>
      </ui-card>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { keepPreviousData } from '@tanstack/vue-query'
import UiCard from '@/components/ui/UiCard'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiPagination from '@/components/ui/UiPagination.vue'
import { useCardState } from '@/composables/useCardState'
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

const { data: tournaments, isLoading, isFetching, refetch } = tournamentsQuery
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
  background: var(--line-soft);
}

.tournaments-section,
.tournaments-panel {
  min-width: 0;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.section-head h2 {
  margin: 0.3rem 0 0.45rem;
  font-family: var(--font-display);
  font-weight: 800;
}

.section-head .section-subtitle {
  margin: 0;
}

.tournaments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.9rem;
}

.tournaments-description {
  flex: 1;
  margin: 0;
}

.tournaments-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.tournaments-date {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

@media (max-width: 760px) {
  .tournaments-page {
    padding: 1rem 1rem 2rem;
  }

  .section-head {
    align-items: stretch;
    flex-direction: column;
  }

  .tournaments-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
